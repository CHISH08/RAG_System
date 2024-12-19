docker network create rag_network
docker run --name llm -d --gpus all   -v ~/code/RAG_System/LLM:/models   --network r
ag_network   ghcr.io/ggerganov/llama.cpp:server-cuda   -m /models/Qwen2.5-Coder-14B-Instruct-IQ2_XS.gguf   --port 8000   --host 0.0.0.0   --n-gpu-layers 12