import fire
import json
import requests
import uuid

from llama_index import Document, GPTSimpleVectorIndex

class CLI:
    def ai(self):
        from langchain.agents import load_tools
        from langchain.agents import initialize_agent
        from langchain.agents import Tool
        from langchain.llms import OpenAI

        # set OPENAI_API_KEY in your environment
        llm = OpenAI(temperature=0)

        index_path = "./index_simple.json"

        try:
            index = GPTSimpleVectorIndex.load_from_disk(index_path)
        except FileNotFoundError:
            index = GPTSimpleVectorIndex(documents=[])
            index.save_to_disk(index_path)

        def doc_from_bytes(contents):
            return Document(str(contents),  # for now
                            doc_id=str(uuid.uuid4()))

        def index_file(filename):
            try:
                contents = open(filename).read()
                doc = doc_from_bytes(contents)
                index.insert(doc)
                index.save_to_disk(index_path)
                return f"The file {filename} was indexed successfully."
            except Exception as e:
                return f"The file {filename} could not be indexed due to an error: {e}"

        def index_url(url):
            try:
                contents = requests.get(url).content
                doc = doc_from_bytes(contents)
                index.insert(doc)
                index.save_to_disk(index_path)
                return f"The URL {url} was indexed successfully."
            except Exception as e:
                return f"The URL {url} could not be indexed due to an error: {e}"

        def search_index(query):
            return str(index.query(query))

        tools = [Tool(name="index_file",
                      description="Add a file to the index.",
                      func=index_file),
                 Tool(name="index_url",
                      description="Add a URL to the index.",
                      func=index_url),
                 Tool(name="search_index",
                      description="Search the index using full english sentences.",
                      func=search_index)
                 ]
        agent = initialize_agent(tools,
                                 llm,
                                 agent="zero-shot-react-description",
                                 verbose=True)

        help = """
        Enter a command like:
        - index the file at /tmp/foo.txt
        - index the URL <url>
        - or just a query about the indexed data.
        Use 'Ctrl-C' or 'Ctrl-D' to quit.",
        NB. The bot has no memory for now, so you must be a little more verbose and redundant.
        """

        print("IndexBot online.")
        print("Enter 'help' for help. 'Ctrl-C' or 'Ctrl-D' to exit.")
        print()
        while True:
            prompt = input("> ")
            if prompt.strip() == "":
                continue
            if prompt.strip().lower() == "help":
                print(help)
                continue
            agent.run(prompt)


if __name__ == '__main__':
    fire.Fire(CLI)