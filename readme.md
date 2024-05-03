# Student Assignment Problem [Exercise Session] #

## Project Description ##
This small project serves as an exercise in the course "Advanced Seminar in Operations Management".
The learning goals are as follows:
- Introduce students to the [Gurobi Solver](https://www.gurobi.com/) and its Python API.
- Introduce students to the features of the [PyCharm IDE](https://www.jetbrains.com/de-de/pycharm/)
- Give a brief introduction on how to set up a (MIP) software project, including the usage of a virtual environment and providing 
a `requirements.txt` file for their supervisor
- Discussion of best-practices and alternative approaches (in-class session)

## MIP ##
You can describe your project (or mixed-integer program) in more detail here, if you want to. This is not really necessary, however what is nice:
In this markdown file, you can also use LaTeX syntax:

E.g.:
The aim of the implemented model is to minimize the overall assigned ranks of students and groups to topics:

**The Cauchy-Schwarz Inequality**
$$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$$

{::nomarkdown}$$\sum\limits_{i \in \mathcal{N}}\sum\limits_{t \in \mathcal{T}} (r^s_{it})^2x^s_{it}+\sum\limits_{i \in \mathcal{G}}\sum\limits_{t \in \mathcal{T}} (r^g_{it})^2 \mathcal{K}_g x^g_{it}$${:/}

## How to setup and run the project ##
This is a very relevant part, please use this section to let your supervisor know how to setup the project and how to replicate the computational study
You can also reference files of your project such as the [requirements-file](requirements.txt) or the [data folder](data) and its contents, e.g. [student file](data/students.json).

1. Install the necessary dependencies via `pip install -r requirements.txt`
2. Place relevant data in the [data folder](data)
3. Run the script `main_for_students.py`