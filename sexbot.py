import fire
import json

def name_from_description(description):
    from langchain.llms import OpenAI
    llm = OpenAI(temperature=0)
    return llm(f"Generate an all lower snake-case (python style) name for a function that fits this description: {description}")

def empty(brain):
    # TODO more sophisticated
    return {k: None for k in brain.keys()}

def generate_func(brain, name, description):
    from langchain.agents import Tool
    from langchain.llms import OpenAI

    emptied = empty(brain)

    llm = OpenAI(temperature=0)
    result = llm(f"Generate a python function called '{name}' that accepts a brain of this shape '{emptied}' and fits this description: {description}")
    print(result)
    space = exec(result, globals())  # XXX !!!!!!
    import ipdb; ipdb.set_trace()
    func = globals()[name]
    return func

def strip_quotes(s):
    while s[0] == "'" and s[-1] == "'":
        return strip_quotes(s[1:-1])
    return s

class CLI:
    def ai(self, streamlit=False):
        from langchain.agents import load_tools
        from langchain.agents import initialize_agent
        from langchain.agents import Tool
        from langchain.llms import OpenAI

        brain = {}

        def add_brain_field(name_and_value):
            name_and_value = strip_quotes(name_and_value)
            (name, value) = name_and_value.split(":")
            try:
                brain[name] = eval(value)  # XXX !!!!!!
            except SyntaxError:
                brain[name] = value
            return f"Added field '{name}' to brain with value: {value}"

        def read_brain_field(name):
            try:
                return f"Field '{name}' has value: {brain[name]}"
            except KeyError:
                return f"Field '{name}' not found in brain."

        def read_whole_brain(*args):
            return f"Brain is:\n\n{json.dumps(brain, indent=4)}"

        tools = []
        def add_new_tool(description):
            name = name_from_description(description)
            func = generate_func(brain, name, description)
            tools.append(Tool(name=name,
                              description=description,
                              func=func))
            return f"Added new tool '{name}' to the agent."

        # set OPENAI_API_KEY in your environment
        llm = OpenAI(temperature=0)

        tools.extend([Tool(name="add_brain_field",
                           description="Pass 'n:v' to add a field named 'n' with a value 'v' to the brain.",
                           func=add_brain_field),
                      Tool(name="read_brain_field",
                           description="Pass a name to read the value stored at that name",
                           func=read_brain_field),
                      Tool(name="request_new_tool",
                           description="Describe a new tool to be added in real time",
                           func=add_new_tool),
                      Tool(name="read_whole_brain",
                           description="Read the whole brain",
                           func=read_whole_brain),
                      Tool(name="read_brain_fields",
                           description="Read the names of the fields of the brain",
                           func=lambda *args: f"Brain fields are: {list(brain.keys())}")
                      ])
        agent = initialize_agent(tools,
                                 llm,
                                 agent="zero-shot-react-description",
                                 verbose=True)
        while True:
            print("sexbot ready.  'Ctrl-C' or 'Ctrl-D' to exit.")
            cmd = input("> ")
            agent.run(cmd)

if __name__ == '__main__':
    fire.Fire(CLI)