# create a user_interface system that allows you to type in your symptoms and it runs a check for matches
# offers the user a list of potential diseases, and creates a similarity graph using these potential diseases
# with counts for each
# users answers creates a list of possible diseases -> call fetch data to get info for each disease
# used fetched data to call visualize graph and create a chart for the user that shows cases and the similarities between diseases
from disease_symptoms import disease_symptoms
from disease_symptoms import unique_symptoms
from disease_symptoms import state_abbreviations
from fetch_rt_data import fetch_data
from build_graph import build_and_plot_graph

def main():
    symptoms = []
    matching_diseases = set()

    print("Hello, Welcome to Disease Aware. Input your symptoms and our system will offer condtions you may be facing\n")
    print("DISCLAIMER: This recommendation system is only based on listed symptoms and should not be used to diagnose a disease.\n")
    print("Please insert your symptoms one by one, when you are done, type 'done'\n")
    print("If you would like to see a list of symptoms in our database, type 'symptoms'\n")
    while(True):
        symptom = input("Insert your symptom here: ")

        if symptom == 'done':
            print("\nYour listed symptoms are:\n")
            for symptom in symptoms:
                print(symptom)
            break
        elif symptom == 'symptoms':
            for symptom in unique_symptoms:
                print(symptom)
        elif symptom.lower() not in unique_symptoms:
            print("Sorry, that symptom is not in our database, you can check all potential symptoms by typing 'symptoms'")
        else:
            symptoms.append(symptom)

    for symptom in symptoms:
        for disease in disease_symptoms:
            if disease not in matching_diseases:
                if symptom in disease_symptoms[disease]:
                    matching_diseases.add(disease)

    
    for disease in matching_diseases:
        print(disease)

    print("\nListed above are some diseases that match your symptoms\n")

    if not matching_diseases:
        print("There are no matching diseases in our database for your symptoms.")

    # pause for user input
    print("For the following question, type (yes/no)")
    graph_bool = input("Would you like to make a graph of potential diseases based on search trends in the U.S?: ")

    if graph_bool == 'yes':
        print("\n")
        while(True):
            state_abbr = input("Please enter the abbreviation for the state you live in (uppercase): ")
            if state_abbr in state_abbreviations:
                break
            else:
                print("\nThe abbreviation you entered is not in our list of US states\n")

        # use function to get disease data for each disease
        print("\nFetching recent data on diseases that match your symptoms... (This may take a few minutes)\n")
        fetch_data(matching_diseases, state_abbr)
        plot_ret = build_and_plot_graph(state_abbr)
        if plot_ret == 1:
            print("There were not enough potential disease to create an effective plot")
        else:
            print("A graph of potential diseases along with trends has now been made in the file your_disease_graph.png")
    
    print("Thank you for using Disease Aware, if you would like to check your symptoms again rerun the symptom_check.py file")

    

if __name__ == "__main__":
    main()
