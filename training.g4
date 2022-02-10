grammar training;

sessions: session+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press'| 'Overhead press' | NAME;
exercise_name : EXERCISE_NAME;
NAME: ALPHABET+ (WS+ ALPHABET+)*;

reps: INT 'k' ;
INT: DIGIT+;
session:
    exercise_name reps NEWLINE
    | exercise_name reps ':'? mini_reps NEWLINE
    | exercise_name ':'? mini_reps NEWLINE;



mini_reps:
    single_reps mini_reps*
    | group_of_reps mini_reps*
    | whole_reps mini_reps*;

whole_reps: INT 'x' INT 'x' INT 'k';
group_of_reps: INT 'x' INT;
single_reps: INT (',' mini_reps)*;

fragment DIGIT: '0'..'9' ;

ALPHABET: [a-zA-Z] ;
NEWLINE:'\r'? '\n' ;
WS:   [ \t]+ -> skip;
