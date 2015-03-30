

* https://www.personadeinteres.org/personas/1760
* http://api.corpwatch.org/ 



is_a = Predicate('type', 'Type', 'is a', implicit=False)
label = Predicate('label', 'Label', 'is called', implicit=True)
alias = Predicate('alias', 'Alias', 'is also known as', implicit=False)
url = Predicate('url', 'URL', 'is described at', implicit=True)
identity = Predicate('identifier', 'Identifier', 'is identified as',
                     implicit=True)

# company
jurisdiction = Predicate('jurisdiction', 'Jurisdiction',
                         'in the jurisdiction', implicit=True)
company_number = Predicate('company_number', 'Company number',
                           'with the company number', implicit=True)
company_type = Predicate('company_type', 'Company type',
                         'has the legal form', implicit=True)

# officer
officer_of = Predicate('officer', 'Officer', 'is an officer of')
position = Predicate('position', 'Position', 'with the role', implicit=True)
start_date = Predicate('start_date', 'Start date', 'started at', implicit=True)
end_date = Predicate('end_date', 'End date', 'ended at', implicit=True)
