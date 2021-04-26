# Connect-Four-AI
Connect Four AI

The original goal of this project was to create an AI capable of playing against a human
player in the game Connect Four. The goal of the game is to get 4 pieces to line up in a grid
whether that be horizontally, vertically, or diagonally. This meant that ideally the AI would try
to achieve this matching in a fewer number of turns than the enemy player could while at the
same time actively trying to stop the enemy player from winning. It was going to use a minimax
algorithm to achieve this as the game has rather easily mappable states and setting rewards for
each should be manageable.

Once I finished the base game implementation in Python using the pygame module, I
implemented the AI using the minimax algorithm as I originally intended but soon found out
that was far too inefficient to work. What I failed to take into account was that connect four
actually has an extremely large number of possible states. The board sized I used was 6 rows by
7 columns, meaning there were 42 different possible points a piece could go into. Without
getting into the calculations, this turns out to mean there are 4531985219092 or
4.531985219092 x 1012 different possible board states. I attempted to see if I could wait for the
AI to place one piece after the human player moves once but had to stop the attempt when no
progress was made after two hours. To circumvent this issue of 4.5 trillion board states I had to
use a more efficient version of the minimax algorithm. Alpha-beta pruning allowed for the
paths that are completely undesirable (which happen to be most of them) to be cutoff and not
explored. This greatly improved performance but it was still far too slow. I was able to run the 
same experiment that previously failed after two hours in about seven minutes, a substantial
improvement but still not enough.

Realizing these inefficiencies, I once again sought out to optimize the AI. This time I
added a transposition table which would be updated each time a reward state is successfully
calculated. This meant a cache would be built of all the previously calculated moves, meaning
there’d be no need to calculate them again. With this method after the first couple of moves
(Specifically the placing of a piece in each of the seven empty columns in the bottom row) the
game went far quicker. Once it was trained by playing against it a couple of times, each starting
a different way, the runtime went from about seven minutes per turn to about two seconds.
This finally made it a viable game. The alpha-beta pruning algorithm combined with the
transposition table were able to make the game far more efficient than minimax would be
alone. The only downside to this implementation is the cache would grow to rather large sizes.
At one point it was 323MB large but by utilizing some compression I was able to get it down to
about 18MB large.
