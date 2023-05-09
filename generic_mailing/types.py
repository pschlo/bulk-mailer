from person import Person

Reply = tuple[int, bytes]
SendErrs = dict[Person, Reply]
SendSuccs = set[Person]