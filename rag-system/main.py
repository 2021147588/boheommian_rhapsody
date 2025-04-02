from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from rag_components import RAGSystem

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG 시스템 초기화
rag_system = RAGSystem()

class Document(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    id: str = ""

class Query(BaseModel):
    text: str

@app.post("/add_documents")
async def add_documents(documents: List[Document]):
    try:
        rag_system.add_documents([doc.dict() for doc in documents])
        return {"message": "Documents added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(query: Query):
    try:
        response = rag_system.generate_response(query.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 