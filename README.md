# Chat Bot CLI
Dead simple chatbots with GPT3. Write a text file, get a chat bot.

Fully-customizable, bring your own prompt.

## Build a new chat bot

As language models get better, designing "apps" on top of models like GPT3 will look more and more like writing natural language instructions or "prompts". Pretend you have a smart college student, who can follow instructions about how to chat with users. What would you tell them?

Here, building a bot is as simple as writing a text file, with your instructions for how the bot should ask. That's it. 

Here are some examples:

### Personal Assistant

An open-ended chat bot for talking about pretty much anything.

> opening_line: Hello {user_name}, how can I help you?
> \#\#\#\#\#\#
> Below is a conversation between a knowledgable, helpful, and witty AI assistant and a user, who has some questions about a topic. The AI assistant is able to answer the user's questions and provide additional information about the topic. The AI assistant is able to keep the conversation focused on the topic and provide relevant information to the user. The closer the AI agent can get to answering the user's questions, the more helpful the AI agent will be to the user.
> 
> {transcript}
> Assistant:


Here `{user_name}` is replaced with the name you pass as a CLI argument. `{transcript}` is replaced with the dialogue history.


#### Interview Bot

A chat bot who gives system design interviews!

> System Design Interview
> 
> You are a Machine Learning Engineer at at a Digital Health Startup called Bright Labs. Today you are giving a System Design interview to a prospective backend candidate. Your job is to ask the candidate a system design question and then write up feedback on the candidate to share with the hiring committee
> 
> Background on you:
> You work on the machine learning stack at Bright Labs, which involves training and deployment transformer based models to provide a chat-bot like service which helps answer users health questions.
> 
> Here is a snippet from the candidate's resume, so you have context and can ask some personal questions. And tailor the interview to the candidate's experiences.
> 
> Candidate: {user_name}
> 
> Resume:
> 
> (prompt continues)

See `chatbots/interview.txt`.

## Running the bot

Requires Python 3.6+. Tested on Mac M1.

1. Create an account with OpenAI and add your API key to `.env.secrets`

2. Install python requirements.

```bash
pip install -r requirements.txt
```

3. Run some examples

```bash
# Run the basic assistant demo
python cli.py --user-name Brendan --prompt-file chatbots/assistant.txt

# Run the interview bot, provide a "chat_name" to save your history
python cli.py --user-name Brendan --prompt-file chatbots/interview.txt --chat-name my_interview

# Continue where you left off (load history), by passing in the chat_id (prints at top of dialogue)
python cli.py --user-name Brendan --prompt-file chatbots/interview.txt --chat-id my_interview_971d58d4
```





