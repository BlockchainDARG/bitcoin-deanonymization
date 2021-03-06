# bitcoin-deanonymization

This code creates a dataset of timestamps and sources for a given, 
data-provided graph. There are two facets to the code: generating
data and training a neural network (through TensorFlow). 

1) To create a dataset, here's an example call:

python generate_data.py -t 300000

Flags:
	-t 		number of trials
	-r 		run number. This is used if we generate more than one 
				dataset due to memory limitations
				[This flag is not yet implemented]
	-s 		type of spreading: (0) Diffusion (default), (1) Trickle
				[This flag is not yet implemented]

Generates a dataset of 300,000 data items. Each item represents a
single simulation of a diffusion process, associated with the true
source node (this is the output label). 


2) To train a neural network, here's an example call:

python fully_connected_feed.py --max_steps 1000000
or 
python fully_connected_feed.py --max_steps 1000000 --restore

Flags:
	--max_steps 		(int) number of iterations for training
	--restore			(no argument) restores the previously 
							trained model (in directory 'logs')
							and continues training
	--batch_size		(int) batch size in each training step
	--hidden1			(int) number of nodes in first hidden
							layer
	--hidden2			(int) number of nodes in second hidden
							layer
