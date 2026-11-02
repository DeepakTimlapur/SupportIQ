from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "documents" / "conversations"

# Every answer below is grounded in the existing ShopEase demo documents.
facts = [
    {
        "category": "shipping",
        "source": "shipping_policy.md",
        "topic": "Standard delivery time",
        "answer": "Standard shipping takes 3 to 7 business days.",
        "followup": "Are these calendar days?",
        "followup_answer": "The published standard-shipping estimate is 3 to 7 business days.",
        "questions": [
            "How long does standard shipping take?",
            "When should I expect my standard delivery?",
            "What is the normal delivery time?",
            "How many business days does regular shipping require?",
            "What is the estimated standard shipping duration?"
        ]
    },
    {
        "category": "shipping",
        "source": "shipping_policy.md",
        "topic": "Express delivery time",
        "answer": "Express shipping takes 1 to 3 business days.",
        "followup": "Is express shipping faster than standard shipping?",
        "followup_answer": "Yes. Express shipping is estimated at 1 to 3 business days, compared with 3 to 7 business days for standard shipping.",
        "questions": [
            "How long does express shipping take?",
            "What is the express delivery estimate?",
            "When will an express order arrive?",
            "How many business days does express delivery need?",
            "What is the delivery time for express shipping?"
        ]
    },
    {
        "category": "shipping",
        "source": "shipping_policy.md",
        "topic": "Free shipping eligibility",
        "answer": "ShopEase offers free shipping on orders above ₹999.",
        "followup": "Do orders below that amount qualify?",
        "followup_answer": "The free-shipping threshold is above ₹999. Orders below that threshold have a standard shipping charge of ₹49.",
        "questions": [
            "What is the minimum order value for free shipping?",
            "When do I qualify for free delivery?",
            "Is shipping free on orders above ₹999?",
            "How much should I order to get free shipping?",
            "What is the free shipping threshold?"
        ]
    },
    {
        "category": "shipping",
        "source": "shipping_policy.md",
        "topic": "Standard shipping fee",
        "answer": "Standard shipping costs ₹49 for orders below the free-shipping threshold.",
        "followup": "Can I avoid this charge?",
        "followup_answer": "The policy offers free shipping on orders above ₹999.",
        "questions": [
            "How much is standard shipping?",
            "What is the regular delivery charge?",
            "How much shipping fee applies below ₹999?",
            "What is the standard shipping cost?",
            "Do I pay ₹49 for standard delivery?"
        ]
    },
    {
        "category": "shipping",
        "source": "shipping_policy.md",
        "topic": "Express shipping fee",
        "answer": "Express shipping costs ₹99.",
        "followup": "How long does express delivery take?",
        "followup_answer": "Express shipping takes 1 to 3 business days.",
        "questions": [
            "What is the express shipping charge?",
            "How much extra does express delivery cost?",
            "What is the price of express shipping?",
            "Do you charge ₹99 for express delivery?",
            "How much do I pay for faster shipping?"
        ]
    },
    {
        "category": "returns",
        "source": "return_refund_policy.md",
        "topic": "Return window",
        "answer": "Customers can request a return within 7 calendar days.",
        "followup": "Does the return period use business days?",
        "followup_answer": "The policy specifies 7 calendar days for the return window.",
        "questions": [
            "How many days do I have to return a product?",
            "What is the return period?",
            "Can I return an item within seven days?",
            "How long is the return window?",
            "When does the return eligibility period end?"
        ]
    },
    {
        "category": "returns",
        "source": "return_refund_policy.md",
        "topic": "Return conditions",
        "answer": "Returned products must be unused and in their original packaging.",
        "followup": "Can I return a used product?",
        "followup_answer": "The stated return conditions require the product to be unused and in its original packaging.",
        "questions": [
            "What condition should a product be in for a return?",
            "Can I return an opened or used item?",
            "Is original packaging required for returns?",
            "What are the return eligibility conditions?",
            "Do returned products need to be unused?"
        ]
    },
    {
        "category": "returns",
        "source": "return_refund_policy.md",
        "topic": "Refund processing time",
        "answer": "Approved refunds are processed within 5 to 7 business days after inspection.",
        "followup": "When does the refund processing period begin?",
        "followup_answer": "The stated 5 to 7 business day period begins after the return inspection is completed and approved.",
        "questions": [
            "How long does a refund take?",
            "When will I receive my refund?",
            "What is the refund processing time?",
            "How many business days are needed for an approved refund?",
            "When are approved returns refunded?"
        ]
    },
    {
        "category": "returns",
        "source": "return_refund_policy.md",
        "topic": "Refund approval",
        "answer": "Returned products are inspected after they reach the warehouse. Refunds are initiated only after the return inspection is approved.",
        "followup": "Is a refund automatic as soon as I ship the item?",
        "followup_answer": "No. The policy states that the returned product is inspected at the warehouse and the refund is initiated after approval.",
        "questions": [
            "What happens after my returned product reaches the warehouse?",
            "When is my refund approved?",
            "Is the refund issued before product inspection?",
            "Does the warehouse inspect returned products?",
            "What is the refund approval process?"
        ]
    },
    {
        "category": "returns",
        "source": "return_refund_policy.md",
        "topic": "Damaged or incorrect item reporting",
        "answer": "Customers should report a damaged or incorrect product within 48 hours and provide photos.",
        "followup": "What should I include in the report?",
        "followup_answer": "The policy asks customers to provide photos when reporting a damaged or incorrect product.",
        "questions": [
            "What should I do if my product arrives damaged?",
            "How soon must I report an incorrect item?",
            "Can I report a damaged delivery after two days?",
            "Do I need photos for a damaged product complaint?",
            "What is the process for reporting a wrong product?"
        ]
    },
    {
        "category": "cancellation",
        "source": "cancellation_policy.md",
        "topic": "Cancellation before dispatch",
        "answer": "An order can be cancelled before it has been dispatched.",
        "followup": "Can I cancel an order that has already shipped?",
        "followup_answer": "The cancellation policy allows cancellation before dispatch. For an order that has already been dispatched, contact support.",
        "questions": [
            "Can I cancel my order before it ships?",
            "When am I allowed to cancel an order?",
            "Can an order be cancelled before dispatch?",
            "What is the order cancellation rule?",
            "How do I know if my order is eligible for cancellation?"
        ]
    },
    {
        "category": "cancellation",
        "source": "cancellation_policy.md",
        "topic": "Cancellation after dispatch",
        "answer": "If an order has already been dispatched, customers should contact support.",
        "followup": "Does the policy guarantee cancellation after dispatch?",
        "followup_answer": "The policy instructs customers to contact support after dispatch; it does not guarantee cancellation at that stage.",
        "questions": [
            "What should I do if my order has already shipped?",
            "Can support help after an order is dispatched?",
            "How do I handle a cancellation after dispatch?",
            "My order has shipped. What should I do?",
            "Who should I contact for a dispatched order cancellation?"
        ]
    },
    {
        "category": "payments",
        "source": "payment_faq.md",
        "topic": "Supported payment methods",
        "answer": "ShopEase supports UPI, credit and debit cards, and net banking.",
        "followup": "Can I pay using UPI?",
        "followup_answer": "Yes. UPI is one of the supported payment methods.",
        "questions": [
            "Which payment methods are supported?",
            "Can I pay using UPI or a card?",
            "Do you accept net banking?",
            "What payment options are available?",
            "Can I use a debit card to pay?"
        ]
    },
    {
        "category": "payments",
        "source": "payment_faq.md",
        "topic": "Failed payment",
        "answer": "For a failed payment, customers should contact support.",
        "followup": "What if money was deducted?",
        "followup_answer": "The payment FAQ instructs customers to contact support for failed or problematic payment transactions.",
        "questions": [
            "What should I do if my payment fails?",
            "My payment did not go through. What now?",
            "How do I report a failed transaction?",
            "What happens when checkout payment fails?",
            "Who should I contact about a failed payment?"
        ]
    },
    {
        "category": "payments",
        "source": "payment_faq.md",
        "topic": "Double charge",
        "answer": "Customers should contact support if they see a duplicate or double charge.",
        "followup": "Should I make another payment?",
        "followup_answer": "The FAQ says to contact support about a double charge. It does not provide an instruction to make another payment.",
        "questions": [
            "I was charged twice. What should I do?",
            "How do I report a duplicate payment?",
            "What if the same order was charged two times?",
            "I see two charges for one purchase. Who can help?",
            "How should I handle a double debit?"
        ]
    },
    {
        "category": "payments",
        "source": "payment_faq.md",
        "topic": "Demo payment reversal",
        "answer": "For the demo payment process, a reversal takes 5 to 7 business days.",
        "followup": "Is that the same as a confirmed refund?",
        "followup_answer": "This 5 to 7 business day reversal timeline is specifically stated for the demo payment process. Refunds for returned products follow the separate return and refund policy.",
        "questions": [
            "How long does a demo payment reversal take?",
            "When will a failed demo payment be reversed?",
            "What is the payment reversal timeline?",
            "How many days does a demo transaction reversal need?",
            "When should I expect a demo payment reversal?"
        ]
    },
    {
        "category": "account",
        "source": "account_faq.md",
        "topic": "Forgot password",
        "answer": "Use the Forgot Password option and follow the instructions sent to your registered email address.",
        "followup": "Which email address should I use?",
        "followup_answer": "Use the email address registered with your ShopEase account.",
        "questions": [
            "I forgot my password. How can I reset it?",
            "How do I recover access to my account?",
            "Where can I reset my ShopEase password?",
            "What should I do if I cannot remember my password?",
            "How can I use the password recovery option?"
        ]
    },
    {
        "category": "products",
        "source": "product_catalog.md",
        "topic": "SmartWatch X1 battery",
        "answer": "The SmartWatch X1 has a battery life of up to 7 days.",
        "followup": "Is seven days guaranteed for every user?",
        "followup_answer": "The product catalog states up to 7 days of battery life; actual usage may vary and the catalog does not guarantee an exact duration for every user.",
        "questions": [
            "How long does the SmartWatch X1 battery last?",
            "What is the battery life of SmartWatch X1?",
            "Can the SmartWatch X1 last seven days?",
            "How many days of battery backup does the X1 offer?",
            "Tell me about the SmartWatch X1 battery."
        ]
    },
    {
        "category": "products",
        "source": "product_catalog.md",
        "topic": "SmartWatch X1 specifications",
        "answer": "The SmartWatch X1 has a 1.8-inch AMOLED display, IP68 water resistance, up to 7 days of battery life, and a 1-year warranty.",
        "followup": "What is its warranty period?",
        "followup_answer": "The SmartWatch X1 has a 1-year warranty according to the product catalog.",
        "questions": [
            "What are the SmartWatch X1 specifications?",
            "Tell me about the SmartWatch X1 features.",
            "Does SmartWatch X1 have an AMOLED display?",
            "What display and water resistance does the X1 offer?",
            "Can you describe the SmartWatch X1?"
        ]
    },
    {
        "category": "products",
        "source": "product_catalog.md",
        "topic": "SoundBeat Pro specifications",
        "answer": "SoundBeat Pro offers up to 30 hours of battery life, 40mm drivers, Bluetooth 5.3, and a 1-year warranty.",
        "followup": "Which Bluetooth version does it support?",
        "followup_answer": "SoundBeat Pro supports Bluetooth 5.3.",
        "questions": [
            "What are the SoundBeat Pro features?",
            "How long does SoundBeat Pro battery last?",
            "Does SoundBeat Pro support Bluetooth 5.3?",
            "What driver size is used in SoundBeat Pro?",
            "Tell me the specifications of SoundBeat Pro."
        ]
    },
    {
        "category": "products",
        "source": "product_catalog.md",
        "topic": "PowerBank 20000 specifications",
        "answer": "PowerBank 20000 has a 20,000mAh capacity, 22.5W output, and a 6-month warranty.",
        "followup": "What is its output rating?",
        "followup_answer": "The PowerBank 20000 is listed with a 22.5W output.",
        "questions": [
            "What is the capacity of PowerBank 20000?",
            "How much power does the PowerBank 20000 provide?",
            "What are the PowerBank 20000 specifications?",
            "Does the 20000 power bank have 22.5W output?",
            "What is the warranty on PowerBank 20000?"
        ]
    },
    {
        "category": "products",
        "source": "product_catalog.md",
        "topic": "AirBuds Lite specifications",
        "answer": "AirBuds Lite offers up to 5 hours of playback per charge, Bluetooth 5.3, and a 1-year warranty.",
        "followup": "Which Bluetooth version is included?",
        "followup_answer": "AirBuds Lite supports Bluetooth 5.3.",
        "questions": [
            "What are the AirBuds Lite specifications?",
            "How long do AirBuds Lite last on one charge?",
            "Does AirBuds Lite support Bluetooth 5.3?",
            "What is the battery playback time of AirBuds Lite?",
            "What warranty comes with AirBuds Lite?"
        ]
    }
]

assert len(facts) == 22
assert all(len(item["questions"]) == 5 for item in facts)

OUT.mkdir(parents=True, exist_ok=True)

created = 0
for fact_number, fact in enumerate(facts, start=1):
    for variation, question in enumerate(fact["questions"], start=1):
        number = (fact_number - 1) * 5 + variation
        slug = re.sub(r"[^a-z0-9]+", "-", fact["topic"].lower()).strip("-")
        filename = f"conversation_{number:03d}_{slug}_{variation}.md"

        content = f"""# Synthetic ShopEase Support Conversation {number:03d}

DATASET: Synthetic demonstration conversation
CATEGORY: {fact['category']}
TOPIC: {fact['topic']}
SOURCE DOCUMENT: {fact['source']}
RECORD ID: SHOP-EASE-DEMO-{number:03d}

## Conversation

**Customer:** {question}

**Support Agent:** {fact['answer']}

**Customer Follow-up:** {fact['followup']}

**Support Agent Follow-up:** {fact['followup_answer']}

## Grounding and safety

This is a synthetic training and retrieval example for the SupportIQ demonstration.
The answers are based on the named ShopEase knowledge-base document.
Do not treat this record as a real customer interaction, transaction, or support case.
If a question requires information not stated in the source policy, consult the source document or escalate to support rather than inventing a policy.
"""
        (OUT / filename).write_text(content, encoding="utf-8")
        created += 1

print(f"Created {created} synthetic conversation files in: {OUT}")
print(f"Categories: {len(set(f['category'] for f in facts))}")
print(f"Unique source-grounded topics: {len(facts)}")
print("Existing policy and product documents were not modified.")


