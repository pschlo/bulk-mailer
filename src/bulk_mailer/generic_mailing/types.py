from person import Emailable

Reply = tuple[int, bytes]
SendErrs = dict[Emailable, Reply]
SendSuccs = set[Emailable]