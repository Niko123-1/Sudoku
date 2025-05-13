def check_duplicates (s: list) -> bool:
    duplicates_flag = False
    s = sorted(s)
    for i in range(0,len(s)):
        if s[i]==s[i-1]:
            duplicates_flag = True
    return duplicates_flag


print(check_duplicates([1,2,3,4,5,6,7,8,9]))