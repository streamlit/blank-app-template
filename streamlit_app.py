print("welcome to the quiz game 🤗")


quiz=[
    ("what is the longest river of the world:", "nile"),
    ("What can travel around the world while staying in the same corner?:", "stamp"),
    ("What has a head and a tail but no body?", "coin"),
    ("What can be seen once in a year, twice in a week, but never in a day? :", "e"),
    ("What kind of room has no doors or windows?", "mushroom")
    ]
score=0
for question, answers in quiz:
     print(question)
     user_answer=input("enter your answer :")
     if user_answer==answers:
        print("you are right ✅:", answers)
       
        score+=1
        print(f"you scored : {score} out of 5 Excellent" )
     else:
        print("wrong ❌:\n", "right answer is :", answers)
        print(score)
 
       
   
def nextqn():
        choice=input("you wannna go to next stage of Quiz (yes or no) :")
        if choice=="yes":
            question2=int(input("choose number 1-5: "))
            if question2==1:
              
                  q1=input("What has hands but can’t clap?: ")
                  if q1=="clock":
                   print("you are correct ✅ :", q1,)
                  else :
                   print("wrong ❌\n", "right answer is :clock")
            if question2==2:
                    q2=input("What gets wetter the more it dries?: ")
                    if q2=="towel":
                     print("you are right ✅ : ", q2)
                    else :
                     print("wrong ❌:\n", "right answer is towel")
            if question2==3:
                     q3=input("What has many keys but can’t open doors?: ")
                     if q3=="piano":
                      print("you are right ✅:", q3)
                     else :
                       print("wrong ❌:\n", "right answer is piano")   
            if question2==4:
                        q4=input("What has one eye but can’t see?: ")
                        if q4=="needle":
                         print("you are right ✅:", q4)
                        else :
                         print("wrong ❌:\n", "right answer is needle") 
            if question2==5:
                            q5=input("What begins with T, ends with T, and has T in it?: ")
                            if q5=="teapot":
                             print("you are right ✅:", q5)
                            else :
                             print("wrong ❌:\n", "right answer is teapot")
                
 
        elif choice=="no":
           print("Thank you for playing QUIZ ❤️")
nextqn()
