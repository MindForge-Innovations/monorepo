from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/messages")
async def receive_message(message_data: dict):
    user_id = message_data.get("userId")
    message = message_data.get("message")
    # Process the message here
    response_message = f"user {user_id} sent '{message}'"
    print("ansewer ", response_message)
    return {"response": response_message}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
