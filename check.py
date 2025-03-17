from google.generativeai import configure, list_models

configure(api_key="AIzaSyDVJdRye4ECAFhpd2Lib7rnv-B-tRl5BPw")

for model in list_models():
    print(model.name)
