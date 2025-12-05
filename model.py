import google.generativeai as genai
genai.configure(api_key="YOUR_API_KEY")

models = genai.list_models()
print(models)
