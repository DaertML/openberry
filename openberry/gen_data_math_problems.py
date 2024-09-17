import json
import requests
import os
import openai

def make_openai(base, prompt):
    client = openai.OpenAI(
        base_url="http://localhost:8080/v1", # "http://<Your api-server IP>:port"
        api_key = "sk-no-key-required"
    )
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": """You are a synthetic data generation agent. Your goal is to generate
a Chain of Thought and rehearsal, in order to solve the user request.

Do not focus on getting the right result; focus on the getting a trace
of the thinking process.

These are the special tokens that you should use:
- <plan></plan>: write your planning to solve the problem between those tags.
- <wait></wait>: after each sentence or thought, run evaluations and rehearsals.
- <think></think>: use this as a scratchpad where you can annotate intermediate results.
- <result></result>: use this to write the answer. This should be a summary of the thinking process.

Here is an example:"""},
        {"role": "problem", "content": """There are 235 books in a library. On Monday, 123 books are taken out. On Tuesday, 56 books are brought back. How many books are there now?"""},
        {"role": "answer", "content":"""<plan>
I should use substraction and addition in order to solve the problem.
I know how to sum numbers.
I know how to substract numbers.
I start with 235 books.
The books that are taken out are substracted.
The books that are brought back are added.
</plan>
<think>
Substract: x = 235 - 123
Add: x = x + 56
</think>
<think>
Steps: 235 - 123
First the first place: 5 - 3 = 2
<wait>
Is 5 - 3 == 2? Yes
</wait>
Result: XXX2
Then the second place: 3 - 2 = 1
<wait>
Is 3 - 2 == 1? Yes
</wait>
Result: XX12
Then the third place: 2 - 1 = 1
Result: X112
Discarding X... 112
</think>
<think>
Adding 112 + 56
First the first place: 6 + 2 = 8
Result: XXX8
Then the second place: 5 + 1 = 6
Result: XX68
Then the third place: 1 + what value?
<wait>
As there is no third place in the second number, it should be 0
</wait>
Then 1 + 0 = 1
Result: X168
Discarding X... 168
</think>
<result>
I have substracted the books that were taken out.
Then added the ones brought back.
There are 168 books.
</result>
"""},
    {"role": "problem", "content": prompt}       
    ]
)
    print(print(completion.choices[0].message.content))
    return completion.choices[0].message.content

def llamacpp_generate(urlllm, prompt, temp=0.6):
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt, "temperature": temp, "n_predict":100}
    data = json.dumps(data)
    res = requests.post(url=urlllm, data=data, headers=headers)
    print(res.json())
    return res.json()["content"]


# Set paths
data_dir = 'data/math/'
questions_folder = 'questions'
solved_folder = 'solved'

# Create solved folder if it doesn't exist
os.makedirs(os.path.join(data_dir, solved_folder), exist_ok=True)

# Get all csv files in questions folder
csv_files = [f'{data_dir}{questions_folder}/{file}' for file in os.listdir(f'{data_dir}{questions_folder}') if file.endswith('.csv')]

prompt_filename = "plan_think_wait_res.txt"
base_prompt = open("./prompts/"+prompt_filename,"r").read()


# Iterate over each csv file and process its content
for file_path in csv_files:
    with open(file_path, mode='r', encoding='utf-8') as file:
        lines = file.readlines()
        
        # Remove '#' separator and pass values one by one to llamacpp function
        prompts = [' '.join(line.split('#')[0:]) for line in lines]
        results = []

        print(prompts)
        for prompt in prompts[:3]:
            #result = llamacpp_generate('http://localhost:8080/completion', prompt)
            result = make_openai(base_prompt, prompt)
            print(result)
            results.append(result)
            
        # Save the results to a new csv file inside solved folder
        output_file_path = f'{data_dir}{solved_folder}/'+prompt_filename.split(".")[0]+"/"+file_path.split("/")[-1] 
        with open(output_file_path, mode='a', newline='', encoding='utf-8') as out_file:
            for res in results:  
                out_file.write(res + '\n')

print("All tasks have been processed.")