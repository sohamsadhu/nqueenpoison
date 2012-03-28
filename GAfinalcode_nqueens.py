''' Program to solve the n Queen by genetic algorithms '''
''' This problem is solvable only for number of queens greater than 3 except where n = 1 '''
''' Author : Soham Sadhu '''

#import the modules from the genetic algorithm framwork to work along
from pyevolve import G1DList, GSimpleGA, Selectors, Statistics, Mutators, Initializators, Crossovers, Consts, DBAdapters
#importing the random modules for the creation of the poison matrix that fills cells randomly as poison
from random import randint, sample
#importing the pyexcelarator module to write the poison and the final best result matrices in the excel sheet 
import pyExcelerator as xl
import os


''' Taking the input form user regarding the number of queens that need to be solved and percentage of cells that need to be poisoned '''

n = int( raw_input('Please enter the number of the queens you want to find solution for: ') )
percentage_poison = int( raw_input('Please enter the percentage of cells that you want poisoned: '))
percentage_poison = int( n * n * percentage_poison *  0.01 )
population = int( raw_input( 'Please enter the population size that you want for evolution: ' ))
generations = int( raw_input( 'Please enter the number of generations you want to evolve: ' ))
crossover_percentage = float( raw_input( 'Please set the crossover percentage: ' ))
crossover_percentage *= 0.01
mutation_percentage = float( raw_input( 'Please set the mutation percentage: ' ))
mutation_percentage *= 0.01
elitism = bool( raw_input( 'Set elitism to True or False: ' ))
data_base = raw_input( 'Enter the data base file name you want : ')
data_base = data_base + '.db'
run_id = raw_input( 'Please associate a id with this evolution run: ')

''' User input ends'''

# setting up the current path
curpath = os.getcwd()

''' Creating the poison cells begin with initialising a 2D array with zeros and then randomly filling in with 1's that are poison cells
Once a poison matrix has been created it reamins same throughout the entire evolution as a static entity.'''
# initialising the poison array with the initial zero elements 
poison_matrix = []
for i in range(n):
   poison_matrix.append([0]*n)

# Making a list range the size of the all element in the poison array
poison = []
for i in range( n * n ):
   poison.append(i)

# choosing the list of the elements randomly that would form the cells to hold poison elements
poison_list = sample(poison, percentage_poison)

# Initialising the poison array with the sample numbers chosen 
for i in range(len(poison_list)):
   x = int( poison_list[i] / n )
   y = int( poison_list[i] % n )
   poison_matrix[x][y] = 1
''' Poison matrix creation ends'''


'''Outputting the poison matrix into a excel file'''

mydoc = xl.Workbook()
sheet1 = run_id + '_poison_sheet'
mysheet = mydoc.add_sheet(sheet1)

#giving the font style for the free, queen and the poison cells
poisonStyle = xl.XFStyle()
queenStyle = xl.XFStyle()
freeStyle = xl.XFStyle()

align = xl.Alignment()
align.horz = xl.Alignment.HORZ_CENTER

# initiliasing the free font style
freeFont = xl.Font()
freeFont.colour_index = 3
freeStyle.alignment = align
freeStyle.font = freeFont

# initialising the poison font style
poisonFont = xl.Font()
poisonFont.colour_index = 2
poisonStyle.alignment = align
poisonStyle.font = poisonFont

#initialising the queen font style
queenFont = xl.Font()
queenFont.colour_index = 4
queenStyle.alignment = align
queenStyle.font = queenFont


for i in range(n):
   for j in range(n):
      if ( poison_matrix[i][j] == 0 ):
         mysheet.write( i, j, 'Free', freeStyle  )
      else:
         mysheet.write( i, j, 'Poison', poisonStyle )
         
mydoc.save(os.path.join(curpath, 'N_queens.ods'))

'''Writing the poison matrix to the excel file ends'''


''' Fitness evaluation function begins, will be used by the frame work to maximise the value that this function sends as a fitness score'''

# chromosome passed to the fitness function is a permutation with the array index as the column and the value at the index row number
# the combination of value and index in the permutation array gives the position of the queen
def eval_func(chromosome):
   
   score = 0
   
   # first for loop checking if the numbers in the permutation do not match if they do then two queens not in same row and score increases
   for i in chromosome:
      for j in chromosome:
         if( i == j ):
            score += 1
            
   # following loop checks if the queens are positioned diagonally and can attack each other if not score increases
   for i in range(len(chromosome)):
      for j in range(len(chromosome)):
         if(abs(chromosome[i] - chromosome[j]) == abs(i-j)):
            score += 1

   # the last loop that checks if the placing of the queen is in the poison cell if yes then add to score 
   for i in range(len(chromosome)):
      if ((poison_matrix[chromosome[i]][i]) == 1):
         score += 1
   
   return score

''' Fitness function evaluation ends '''

'''Callback function which will be called at each evolution step'''
def evolve_callback(ga_engine):
   generation = ga_engine.getCurrentGeneration()
   if generation % 10 == 0:
      print "Current generation: %d" % (generation,)
      print ga_engine.getStatistics()
   return False
'''End of call back function'''


''' Creation of the chromosome or the genotype '''
# Creation of the one dimensional list of numbers that are chromosome that are initialised randomly
genome = G1DList.G1DList(n)
# the range of number that will make up the permutation randomly will be between the zero, minus one the number of queens which will give us the
# their position on the 2D array a abstraction of the chess board
genome.setParams(rangemin=0, rangemax= (n-1))

# Passing the fitness function parameter to the frame work evaluator function 
genome.evaluator.set(eval_func)

''' Change the mutator to Integer Range '''
genome.mutator.set(Mutators.G1DListMutatorIntegerRange)

''' Setting up the cross over parameter for the frame work this will remain constant for this checkpoint 5
and will be experimented in the next check point 6. Right now it is a two point cross over function '''
genome.crossover.set(Crossovers.G1DListCrossoverTwoPoint)
# Initiliasing the evolution algorithm in the frame work that does the evolution 
ga = GSimpleGA.GSimpleGA(genome)

''' selection criteria'''
ga.selector.set(Selectors.GRankSelector)

# Setting the algorithm fitness function to be maximised
ga.minimax = Consts.minimaxType["minimize"]

# the crossover and the mutation rate are kept constant for this checkpoint 
ga.setCrossoverRate(crossover_percentage)
ga.setMutationRate(mutation_percentage)

#Setting the population and the generation size
ga.setPopulationSize(population)
ga.setElitism(elitism)
ga.setGenerations(generations)

#setting the convergence criteria
#ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)
#ga.terminationCriteria.set(GSimpleGA.FitnessStatsCriteria)

'''Instead of using the frequency stats function in evolve function using the callback to give more detailed statistics which
is called at every step of the evolution'''
ga.stepCallback.set(evolve_callback)

''' The following two lines dump all the statistics regarding the individuals and the population into a .DB file that is data base file
which can be read after wards with tool sqlliteman and will help in the drawing the various graphs'''
#Remember to set resetDB to True if a new database is being created. However if writing on a old database
#make resetDB = False since it will over write the database even if the identifiers are different
sqlite_adapter = DBAdapters.DBSQLite( dbname = data_base, identify = run_id, resetDB = True )
ga.setDBAdapter(sqlite_adapter)

''' IMPORTANT: the below line is call to evolution function in the pyevolve framework.
If you want lesser amount of details during the evolution then include parameter freq_stats = number of evolution cycles after which you want the statistics
In this program if you comment the previous callback function you can get rid of excessive statistics.'''
ga.evolve( freq_stats = 20 )

# print the individual with the best fitness
print ga.bestIndividual()

result = ga.bestIndividual()

#n Queen output to a excel file
sheet2 = run_id + 'result_sheet'
mysheet = mydoc.add_sheet(sheet2)

for i in range(n):
   mysheet.col(i).width = 0x0d00 - 2400
   if ( poison_matrix[result[i]][i] == 0 ):
      mysheet.write( result[i], i, 'Q', queenStyle  )
   else:
      mysheet.write( result[i], i, 'Q/P', poisonStyle )
   #mysheet.write( result[i], i, 'Q', poisonStyle )
         
mydoc.save(os.path.join(curpath, 'N_queens.ods'))

 
