from agents_server.embedding.openai_embedding import GetOpenAIEmbeddings

input_data = "世界充满了未知的奥秘"
res = GetOpenAIEmbeddings(input_data)
print(res)
