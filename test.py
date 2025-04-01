from ollama import Client
client = Client(
  #host="https://ollama.molodetz.nl",
  host='http://localhost:8080',
  headers={'x-some-header': 'some-value'}
)

def times_two(nr_1: int) -> int:
    return nr_1 * 2

available_functions = {
    'times_two': times_two
}

messages = []


def chat_stream(message):
    if message:
        messages.append({'role': 'user', 'content': message})
    content = ''
    for response in client.chat(model='qwen2.5-coder:0.5b', messages=messages,stream=True):
        content += response.message.content
        print(response.message.content,end='',flush=True)
    messages.append({'role': 'assistant', 'content': content})
    print("")

def chat(message,stream=False):
    if stream:
        return chat_stream(message)
    if message:
        messages.append({'role': 'user', 'content': message})
    response = client.chat(model='qwen2.5:3b', messages=messages,
    tools=[times_two])
    if response.message.tool_calls:
  # There may be multiple tool calls in the response
        for tool in response.message.tool_calls:
            if function_to_call := available_functions.get(tool.function.name):
                print('Calling function:', tool.function.name)
                print('Arguments:', tool.function.arguments)
                output = function_to_call(**tool.function.arguments)
                print('Function output:', output)
            else:
                print('Function', tool.function.name, 'not found')

# Only needed to chat with the model using the tool call results
            if response.message.tool_calls:
                # Add the function response to messages for the model to use
                messages.append(response.message)
                messages.append({'role': 'tool', 'content': str(output), 'name': tool.function.name})

                # Get final response from model with function outputs
                return chat(None)
    return response.message.content


while True:
    chat_stream("A farmer and a sheep are standing on one side of a river. There is a boat with enough room for one human and one animal. How can the farmer get across the river with the sheep in the fewest number of trips?")

