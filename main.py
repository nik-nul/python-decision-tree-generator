import ast
import graphviz
import textwrap

class DecisionTreeBuilder(ast.NodeVisitor):
    def __init__(self):
        """Initializes the decision tree builder."""
        self.graph = graphviz.Digraph('decision_tree', format='png')
        self.graph.attr('node', shape='box', style='filled', fillcolor='lightblue')
        self.current_node = None
        self.node_counter = 0
        self.suppress_edge = False

    def create_node(self, label, fillcolor='lightblue'):
        """Creates a new graph node with the given label."""
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        wrapped_label = textwrap.fill(label, width=40)
        self.graph.node(node_id, wrapped_label, fillcolor=fillcolor)
        return node_id

    def visit_If(self, node):
        """Processes an 'if' node, its 'if' and 'else' branches."""
        condition_text = ast.unparse(node.test)
        condition_node = self.create_node(f"Condition: {condition_text}")
        parent = self.current_node
        if parent:
            self.graph.edge(parent, condition_node)
        
        true_branch = None
        self.current_node = condition_node
        for stmt in node.body:
            prev = self.current_node
            self.suppress_edge = True
            self.visit(stmt)
            self.suppress_edge = False
            if self.current_node != prev and true_branch is None:
                true_branch = self.current_node
                self.graph.edge(condition_node, true_branch, label="True")
            elif self.current_node != prev:
                self.graph.edge(prev, self.current_node, label="True")
                
        false_branch = None
        self.current_node = condition_node
        for stmt in node.orelse:
            prev = self.current_node
            self.suppress_edge = True
            self.visit(stmt)
            self.suppress_edge = False
            if self.current_node != prev and false_branch is None:
                false_branch = self.current_node
                self.graph.edge(condition_node, false_branch, label="False")
            elif self.current_node != prev:
                self.graph.edge(prev, self.current_node, label="False")
        
        self.current_node = parent

    def visit_Return(self, node):
        """Creates a terminal node for 'return' statements."""
        return_text = ast.unparse(node)
        return_node = self.create_node(return_text, fillcolor='lightgreen')
        if self.current_node and not self.suppress_edge:
            self.graph.edge(self.current_node, return_node)
        self.current_node = return_node

    def generic_visit(self, node):
        """Handles other node types, particularly expressions."""
        if isinstance(node, ast.Expr):
            expr_text = ast.unparse(node)
            expr_node = self.create_node(expr_text, fillcolor='lightyellow')
            if self.current_node and not self.suppress_edge:
                self.graph.edge(self.current_node, expr_node)
            self.current_node = expr_node
        else:
            super().generic_visit(node)

def generate_decision_tree(code, output_file='decision_tree'):
    """
    Generates a decision tree image from Python code containing if, else, and return statements.
    
    Args:
        code (str): Python code as a string.
        output_file (str): Base output filename (without extension).
    
    Returns:
        str: Path to the generated image file.
    """
    try:
        tree = ast.parse(code)
        builder = DecisionTreeBuilder()
        builder.visit(tree)
        builder.graph.render(output_file, cleanup=True)
        return f"{output_file}.png"
    except SyntaxError as e:
        return f"Syntax error: {e}"
    except Exception as e:
        return f"Error: {e}"

def main():
    """Parses command-line arguments and generates the decision tree."""
    import argparse
    parser = argparse.ArgumentParser(description='Generate a decision tree from Python code.')
    parser.add_argument('input_file', help='Path to the Python file containing if-else-return code')
    parser.add_argument('--output', '-o', default='decision_tree', help='Output file basename')
    args = parser.parse_args()
    
    try:
        with open(args.input_file, 'r') as f:
            code = f.read()
        output_path = generate_decision_tree(code, args.output)
        print(f"Decision tree generated: {output_path}")
    except FileNotFoundError:
        print(f"Error: File {args.input_file} not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
