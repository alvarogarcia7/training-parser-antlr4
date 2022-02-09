grammar training_mine;

sessions: session+;

EXERCISE_NAME: 'Deadlift' | 'Squat' | 'Bench press'| 'Overhead press';
exercise_name : EXERCISE_NAME;
//NAME: ALPHABET+ (WS+ ALPHABET+)*;
reps: INT 'k' ;
INT: DIGIT+;
session: exercise_name reps NEWLINE;
fragment DIGIT: '0'..'9' ;


//ALPHABET: [a-zA-Z] ;
NEWLINE:'\r'? '\n' ;
WS:   [ \t]+ -> skip;
