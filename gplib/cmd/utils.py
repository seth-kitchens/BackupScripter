
def prompt_do_continue(continue_text='Continue?'):
    print(continue_text + ' (y/n)\n> ', end='')
    answer = input()
    yes_answers = ['y', 'yes', 'yeah', 'continue']
    return (answer.lower() in yes_answers)

def prompt_any_input(text='Enter any input to continue.'):
    print(text)
    print('> ', end='')
    input()
    return