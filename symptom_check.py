# create a user_interface system that allows you to type in your symptoms and it runs a check for matches
# offers the user a list of potential diseases, and creates a similarity graph using these potential diseases
# with counts for each
# users answers creates a list of possible diseases -> call fetch data to get info for each disease
# used fetched data to call visualize graph and create a chart for the user that shows cases and the similarities between diseases
from disease_symptoms import disease_symptoms
from disease_symptoms import unique_symptoms
from fetch_rt_data import fetch_data

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
            print("Your listed symptoms are")
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

    print("Here are some diseases that match your symptoms:\n")
    for disease in matching_diseases:
        print(disease)

    # use function to get disease data for each disease
    print("Fetching recent data on diseases that match your symptoms...")
    fetch_data(matching_diseases)

if __name__ == "__main__":
    main()
