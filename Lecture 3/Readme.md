For Virtual env use:
To Create:
Mac/Linux: python -m venv <Name>
Windows: python -m venv <Name>
To activate:
Mac/Linux: source <Name>/bin/activate
Windows: <Name>\Scripts\activate
Also add a .env as discussed in the lecture

Then to download the files using requirements.txt use pip install -r requirements.txt

Slides: https://docs.google.com/presentation/d/1TPe2Na7eLQp7Oi-dhZyxfZPso2YLGWGeFQTtn9fSNFM/edit?usp=sharing

Quiz: https://docs.google.com/forms/d/e/1FAIpQLSepamoOwK7J_Tvtt8_k48a4JOW-nZiBVA--ElTlB6NSRo0oxQ/viewform?usp=publish-editor

Check langchain syntax and tut: https://docs.langchain.com/oss/python/langchain/rag

Okay so you all will see torch in the requirements.txt it is because of sentence transformer, try to use a api call to embeding model to implement embeding, because although it will not exceed the api tokens but you will see that when you try to deploy these applications, it exceeds the memory that free service provides, had a hard time at a hackthon, due to this...try to implement.