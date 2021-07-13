
# * The arrays below are used to check if the user is writing in the correct syntax
# * when adding more items to an array, simply put the correct syntax
# * creating a new array for a language is in the following naming convention: correct_LANGNAME_patterns
correct_patterns = {
    "cs": ["Console.WriteLine", "Console.Write","WriteLine", ".Write", ".ReadLine", "int.Parse", r"\.Length", r"\.GetLength" ,"Char.Parse", "Boolean.Parse"],
    "java": ["Scanner(System.in)", "String", "System.in", ".nextInt", "Integer.parseInt", "Boolean.parseBoolean",
             ".toString", ".valueOf", "System."],
    "js": ["console.log"],
}
