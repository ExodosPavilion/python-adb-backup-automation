from pick import pick

#Links
#	https://github.com/wong2/pick

#the pick library allows us to have a simple selection system within the terminal itself

#What to display above the options
title = 'Please choose your favorite programming language (press SPACE to mark, ENTER to continue): '

#What are the options
options = ['Java', 'JavaScript', 'Python', 'PHP', 'C++', 'Erlang', 'Haskell']
options = list(range(1,10))
#create the pick object
#	multiselect: when set to true allows the user to select more than one option
#	min_selection_count: set the minimum number of selections the user has to do
#						 this option has to accompany the multiselect option
selected = pick(options, title, multiselect=True, min_selection_count=1)

optionNames = []
indexes = []

for i in selected:
	optionNames.append(i[0])
	indexes.append(i[1])
	
print(type(optionNames[1]))
print(indexes)