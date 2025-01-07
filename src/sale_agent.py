from sales_agent.sales_conversation import SalesConversation

def main():


    conversation = SalesConversation()

    print("Sales Conversation Bot (type 'quit' to exit, 'save' to save conversation, 'load' to load conversation)")
    print("-" * 50)

    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'save':
            conversation.save_conversation("conversation.json")
            print("Conversation saved to conversation.json")
            continue
        elif user_input.lower() == 'load':
            conversation = SalesConversation.load_conversation("conversation.json",)
            print("Conversation loaded from conversation.json")
            continue
            
        response = conversation.process_message(user_input)
        print("\nBot:", response)

if __name__ == "__main__":
    main()