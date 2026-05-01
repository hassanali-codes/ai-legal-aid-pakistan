from langchain_core.prompts import PromptTemplate

__all__ = ["get_urdu_legal_prompt"]


def get_urdu_legal_prompt():
    template = """
Aap ek Pakistani legal assistant hain jo logon ko
unke qanooni huqooq samjhata hai.

Neeche diye gaye context ko parh kar sawal ka jawab dein.
Agar sawal English mein hai to jawab English mein dein.
Agar sawal Urdu mein hai to jawab Urdu mein dein.
Aap context ki language ko follow kar sakte hain, lekin response hamesha user ke sawal ki language mein hona chahiye.
Agar jawab context mein nahi hai, toh kehein:
"Mujhe is baare mein context nahi mila,
kisi lawyer se rabta karein."

Context:
{context}

Sawal: {question}

Jawab:
"""
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"],
    )