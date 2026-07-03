from agent_models import AgentRequest, EchoAgent, ModeratedAgent

request = AgentRequest(user_id='u-1', message='Summarize the release notes', priority='normal')
for agent in [EchoAgent('echo'), ModeratedAgent('safe_echo')]:
    print(agent.handle(request))
