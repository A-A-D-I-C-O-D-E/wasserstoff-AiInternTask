def build_reply_prompt(email_subject, email_body, thread_history=None):
    context = f"Subject: {email_subject}\n\n"
    if thread_history:
        context += f"Thread History:\n{thread_history}\n\n"
    context += f"Latest Email:\n{email_body}\n\n"
    context += "Write a polite, professional, and helpful reply to this email:"
    return context

from transformers import pipeline

reply_generator = pipeline("text-generation", model="google/flan-t5-large")  # or another

def generate_reply(prompt):
    result = reply_generator(prompt, max_length=300, do_sample=True)
    return result[0]['generated_text']
