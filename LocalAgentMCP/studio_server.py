import uvicorn
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import asyncio
import httpx
import glob
from tool_loader import load_all_tools

# ================= CONFIG =================
PORT = 8000
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
CONFIG_FILE = "ai_config.json"

app = FastAPI(title="Local AI Studio")

# CORS 설정
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Static 폴더 마운트 (이미지 서빙용)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# 로컬 툴 로드
TOOLS = load_all_tools()

# 대화 내역 저장소
history_storage = {}

# ================= HELPER FUNCTIONS =================
def parse_ovos_json(data):
    """OVOS 스타일 JSON을 시스템 프롬프트로 변환"""
    prompt = f"당신은 '{data.get('name')}'입니다. 역할은 '{data.get('role')}'입니다.\n"
    prompt += f"설명: {data.get('description')}\n\n"
    
    prompt += "★★★ 중요: 당신은 실시간 웹 검색 도구(web_search)를 사용할 수 있습니다. 사용자가 최신 정보를 묻거나 당신이 모르는 지식을 물어보면, 절대 '모른다'고 답하지 말고 즉시 'web_search' 도구를 사용하여 정보를 찾아 답변하세요. ★★★\n\n"
    
    if "speech_style" in data:
        style = data["speech_style"]
        prompt += f"[말투 가이드]\n- 톤: {style.get('tone')}\n"
        prompt += f"- 특징: {style.get('sentence_pattern')}\n"
        prompt += "- 예시:\n"
        for ex in style.get("examples", []):
            prompt += f"  * {ex}\n"
    
    if "interaction_rules" in data:
        rules = data["interaction_rules"]
        prompt += "\n[행동 수칙]\n"
        for rule in rules.get("always", []):
            prompt += f"- (항상) {rule}\n"
        for rule in rules.get("never", []):
            prompt += f"- (금지) {rule}\n"
            
    return prompt

def load_character_plugins():
    """캐릭터 플러그인 로드"""
    models = {}
    if not os.path.exists("characters"):
        os.makedirs("characters")
    
    for filepath in glob.glob("characters/*.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                char_id = os.path.basename(filepath).replace(".json", "")
                
                sys_prompt = parse_ovos_json(data) if "speech_style" in data else data.get("system_prompt", "")
                
                models[char_id] = {
                    "name": data.get("base_model", "qwen2.5-coder:14b"),
                    "label": f"{data.get('name', char_id)}",
                    "role_badge": data.get('role', 'Assistant'),
                    "description": data.get('description', ''),
                    "icon": data.get("icon", "fa-user"),
                    "system_prompt": sys_prompt
                }
                if char_id not in history_storage:
                    history_storage[char_id] = []
        except Exception as e:
            print(f"❌ Error loading {filepath}: {e}")
            
    return models

def get_config():
    config = {"models": {}}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
        except:
            pass
    
    config["models"].update(load_character_plugins())
    return config

async def execute_tool(tool_name, args):
    """툴 실행"""
    if tool_name not in TOOLS:
        return f"Error: Tool '{tool_name}' not found."
    
    try:
        handler = TOOLS[tool_name]["handler"]
        print(f"🔧 [Tool Run] {tool_name}")
        
        if asyncio.iscoroutinefunction(handler):
            result = await handler(args)
        else:
            result = await asyncio.to_thread(handler, args)
            
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"

async def analyze_image_with_vision_model(image_base64, prompt="이 이미지를 자세히 설명해줘."):
    """Vision 모델(Llava) 호출"""
    try:
        payload = {
            "model": "llava",
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],
            "stream": False
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(DEFAULT_OLLAMA_URL, json=payload)
            if resp.status_code == 200:
                return resp.json()["message"]["content"]
    except:
        return None
    return None

# ================= API ENDPOINTS =================
@app.get("/")
async def get_ui():
    if os.path.exists("studio.html"):
        with open("studio.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>studio.html not found</h1>")

@app.get("/models")
async def list_models():
    return get_config().get("models", {})

@app.get("/history/{model_id}")
async def get_history(model_id: str):
    return history_storage.get(model_id, [])

# ================= WEBSOCKET CORE =================
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            try:
                # 1. 데이터 수신 및 타입 방어
                data = await websocket.receive_json()
                
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except:
                        continue
                
                if not isinstance(data, dict):
                    continue

            except WebSocketDisconnect:
                break
            except Exception:
                break
            
            user_msg = data.get("message", "")
            files = data.get("files", [])
            model_key = data.get("model", "lucia")
            
            config = get_config()
            if model_key not in config["models"]:
                model_key = list(config["models"].keys())[0] if config["models"] else None
            
            current_model = config["models"].get(model_key)
            if not current_model:
                continue

            if model_key not in history_storage:
                history_storage[model_key] = []

            # 2. 이미지 처리 (Vision Proxy)
            images_processed_context = ""
            for f in files:
                if f['type'] == 'image':
                    await websocket.send_json({"type": "status", "text": "👁️ 이미지를 보는 중..."})
                    vision_result = await analyze_image_with_vision_model(f['content'])
                    if vision_result:
                        images_processed_context += f"\n[이미지 분석 결과: {vision_result}]\n"
                    else:
                        images_processed_context += "\n[시스템: 이미지 분석 실패 (Llava 모델 필요)]\n"
                elif f['type'] == 'text':
                    images_processed_context += f"\n\n--- [파일: {f['name']}] ---\n{f['content']}\n------------------\n"

            final_user_msg = images_processed_context + "\n" + user_msg if images_processed_context else user_msg
            history_storage[model_key].append({"role": "user", "content": final_user_msg})

            # 3. Ollama 호출 준비
            ollama_tools = []
            for name, info in TOOLS.items():
                ollama_tools.append({
                    "type": "function",
                    "function": {
                        "name": name,
                        "description": info.get("description", ""),
                        "parameters": info.get("inputSchema", {})

            try:
                async with httpx.AsyncClient(timeout=180) as client:
                    resp = await client.post(DEFAULT_OLLAMA_URL, json=payload)
                    resp.raise_for_status()
                    
                    # [핵심] 응답 데이터 파싱 및 타입 방어
                    try:
                        resp_data = resp.json()
                    except:
                        resp_data = {}

                    # 문자열로 오면 JSON 파싱 재시도
                    if isinstance(resp_data, str):
                        try:
                            resp_data = json.loads(resp_data)
                        except:
                            resp_data = {"message": {"content": str(resp_data)}}

                    ai_msg = resp_data.get("message", {})

                    # [★여기가 수정됨★] message 필드가 문자열이면 딕셔너리로 변환
                    if isinstance(ai_msg, str):
                        ai_msg = {"content": ai_msg}

                    # 4. 툴 사용 여부 체크
                    if isinstance(ai_msg, dict) and ai_msg.get("tool_calls"):
                        history_storage[model_key].append(ai_msg)
                        
                        for tool_call in ai_msg["tool_calls"]:
                            fn = tool_call["function"]
                            t_name = fn["name"]
                            t_args = fn["arguments"]
                            
                            await websocket.send_json({"type": "status", "text": f"💻 {t_name} 실행 중..."})
                            
                            # 툴 실행
                            tool_result = await execute_tool(t_name, t_args)
                            
                            history_storage[model_key].append({
                                "role": "tool",
                                "content": tool_result,
                            })
                        
                        # 툴 결과 반영 후 재호출
                        payload["messages"] = [{"role": "system", "content": current_model.get("system_prompt", "")}] + history_storage[model_key]
                        del payload["tools"]
                        
                        final_resp = await client.post(DEFAULT_OLLAMA_URL, json=payload)
                        final_data = final_resp.json()
                        
                        final_msg_obj = final_data.get("message", {})
                        if isinstance(final_msg_obj, str):
                            final_msg_obj = {"content": final_msg_obj}
                            
                        final_content = final_msg_obj.get("content", "")
                        
                        history_storage[model_key].append({"role": "assistant", "content": final_content})
                        await websocket.send_json({"type": "answer", "text": final_content})

                    else:
                        # 일반 답변
                        content = ai_msg.get("content", "")
                        history_storage[model_key].append({"role": "assistant", "content": content})
                        await websocket.send_json({"type": "answer", "text": content})

            except Exception as e:
                print(f"Error: {e}")
                await websocket.send_json({"type": "error", "text": f"AI 응답 실패: {str(e)}"})

    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        print("Client disconnected.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)