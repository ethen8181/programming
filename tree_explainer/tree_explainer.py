import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.tree import _tree
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier


def _format_explanation(model, data_row, prediction, contrib, feature_names):
    if isinstance(model, (DecisionTreeClassifier, RandomForestClassifier)):
        best_idx = np.argmax(prediction)
        contrib = contrib[:, best_idx]

    # convert the explanation to dataframe for better interpretation,
    # column names are hard-coded
    value_col = 'value'
    contrib_col = 'contrib'
    feature_col = 'feature'
    explained = {value_col: data_row,
                 contrib_col: contrib,
                 feature_col: feature_names}
    df_explained = pd.DataFrame(explained, columns = [contrib_col, feature_col, value_col])
    df_explained = (df_explained
                    .loc[df_explained[contrib_col] != 0.0]
                    .sort_values(contrib_col, ascending = False)
                    .reset_index(drop = True))

    pred_info = {'predict': prediction}
    if isinstance(model, (DecisionTreeClassifier, RandomForestClassifier)):
        pred_info = {'predict': best_idx, 'predict_proba': prediction}

    return df_explained, pred_info


class DecisionTreeExplainer:
    """docstring for ClassName"""
    def __init__(self, model_tree, feature_names):
        self.model_tree = model_tree
        self.feature_names = feature_names

        # map leaves to paths, and reverse the path so
        # that the sequence starts with the root node (node_id = 0)
        paths = self._get_tree_paths(tree = self.model_tree.tree_, node_id = 0)
        leaf_to_path = {}
        for path in paths:
            path.reverse()
            leaf_to_path[path[-1]] = path

        # obtain the prediction value at each node,
        # remove the single-dimensional inner arrays
        values = self.model_tree.tree_.value.squeeze()
        if isinstance(self.model_tree, DecisionTreeRegressor):
            contribs_shape = self.model_tree.n_features_
        elif isinstance(self.model_tree, DecisionTreeClassifier):
            # sklearn classification tree's value stores class counts
            # at each node id, we turn them into probabilities
            normalizer = np.sum(values, axis = 1, keepdims = 1)
            values /= normalizer
            contribs_shape = self.model_tree.n_features_, self.model_tree.n_classes_

        self._unique_contribs = self._compute_contrib(values, leaf_to_path, contribs_shape)

        # the bias is always simply the value at the root node
        self._values = values
        self.bias_ = values[0]

        # TODO: ??? the attribute is used to return different value
        # when using the class in the RandomForestExplainer;
        # might need to evaluate whether this is the best way
        self._ensemble_tree = False

    def explain(self, data_row):
        """
        Parameters
        ---------
        data_row: 1d nd.array
            corresponding to a row
        """

        # return the index of the leaf each data points ends up in
        # and obtain prediction for each observation
        # by using which leaf it belongs to;
        # prediction is essentially the same as calling
        # self.model_tree.predict_proba(X) for classification tree
        # or self.model_tree.predict(X) for regression tree
        X = np.atleast_2d(data_row)
        leaf = self.model_tree.apply(X)[0]
        contrib = self._unique_contribs[leaf]
        prediction = self._values[leaf]

        if not self._ensemble_tree:
            df_explained, pred_info = _format_explanation(
                self.model_tree, data_row, prediction, contrib, self.feature_names)

            return df_explained, pred_info
        else:
            return prediction, contrib, self.bias_

    def _get_tree_paths(self, tree, node_id):
        """
        returns all paths through the tree as list
        of node_ids, note that the path here will
        be the sequence of nodes from the leaf node
        to the root node
        """
        left_node = tree.children_left[node_id]
        right_node = tree.children_right[node_id]

        if left_node != _tree.TREE_LEAF:
            left_paths = self._get_tree_paths(tree, left_node)
            right_paths = self._get_tree_paths(tree, right_node)

            for path in left_paths:
                path.append(node_id)

            for path in right_paths:
                path.append(node_id)

            paths = left_paths + right_paths
        else:
            paths = [[node_id]]

        return paths

    def _compute_contrib(self, values, leaf_to_path, contribs_shape):
        """
        compute the contribution vector for each unique tree leaf nodes
        and store the result into a dictionary, whose keys are leaf nodes
        and the corresponding value refers to the contribution vector of the leaf node.
        after that we can simply assign the contribution vector to each observation
        by looking up which leaf node it is assigned
        """

        # convert numpy array into python list,
        # accessing values will be faster
        # https://stackoverflow.com/questions/35020604/why-is-numpy-list-access-slower-than-vanilla-python
        values = list(values)

        # feature[i] holds the feature to split on,
        # for the internal node i
        feature = list(self.model_tree.tree_.feature)

        unique_contribs = {}
        for leaf, path in leaf_to_path.items():
            # compute the contribution of each feature
            # for a given observation
            contribs = np.zeros(contribs_shape)
            for depth in range(len(path) - 1):
                contrib = values[path[depth + 1]] - values[path[depth]]
                feature_idx = feature[path[depth]]
                contribs[feature_idx] += contrib

            unique_contribs[leaf] = contribs

        return unique_contribs


class RandomForestExplainer:
    """docstring for ClassName"""
    def __init__(self, model_rf, feature_names, n_jobs = -1,
                 verbose = True, pre_dispatch = '2*n_jobs'):
        self.n_jobs = n_jobs
        self.verbose = verbose
        self.model_rf = model_rf
        self.pre_dispatch = pre_dispatch
        self.feature_names = feature_names

        # TODO : ???
        # move the computing contribution to init to
        # only perform the computation once, and future
        # explain will only be a fast lookup

    def explain(self, data_row):
        """
        Parameters
        ---------
        data_row: 1d nd.array
            corresponding to a row
        """

        # average the contribution for each individual trees
        parallel = Parallel(n_jobs = self.n_jobs, verbose = self.verbose,
                            pre_dispatch = self.pre_dispatch)
        output = parallel(delayed(self._explain_model_tree)(data_row, model_tree,
                                                            self.feature_names)
                          for model_tree in self.model_rf.estimators_)

        predictions, contribs, biases = zip(*output)

        if isinstance(self.model_rf, RandomForestClassifier):
            self.bias_ = np.mean(biases, axis = 0)
            prediction = np.mean(predictions, axis = 0)
        elif isinstance(self.model_rf, RandomForestRegressor):
            self.bias_ = np.mean(biases)
            prediction = np.mean(predictions)

        contrib = np.mean(contribs, axis = 0)

        df_explained, pred_info = _format_explanation(
            self.model_rf, data_row, prediction, contrib, self.feature_names)

        return df_explained, pred_info

    def _explain_model_tree(self, data_row, model_tree, feature_names):
        # modify the private attribute so we can get all the information that
        # is needed for the ensemble tree explainer
        tree_explain = DecisionTreeExplainer(model_tree, self.feature_names)
        tree_explain._ensemble_tree = True
        prediction, contrib, bias = tree_explain.explain(data_row)
        return prediction, contrib, bias


__all__ = ['DecisionTreeExplainer', 'RandomForestExplainer']
