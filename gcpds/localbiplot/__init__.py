# example.py

"""
============
local biplot
============
"""


# def greet(name):
#     """
#     This function greets the person whose name is passed as a parameter
#     """
#     return f"Hello, {name}!"

# if __name__ == "__main__":
#     print(greet("World"))

# libraries_to_install = {'adjustText': 'adjustText'} #'adjustText': 'adjustText',  'umap-learn': 'umap'

# for library, alias in libraries_to_install.items():
#     try:
#         exec(f"import {alias}")
#     except ImportError:
#         pip install {library} --quiet


#librerias a importar

import os
import warnings
warnings.filterwarnings("ignore")


import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm

import pandas as pd
import seaborn as sns
from seaborn import kdeplot

from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN

from scipy.spatial.distance import cdist, squareform
from scipy.stats import multivariate_normal
from scipy.optimize import minimize
from scipy import interpolate

#from adjustText import adjust_text



# Objeto para guardar resultados:
class GMDOutput:
    pass

#centering kernels
class LocalBiplot(): #Poner en CamelCase

    """
    Object for data analysis using linear and non-linear Biplots obtained by
    SVD decomposition and a Generalized SVD decomposition .

    This class implements a set of functions for data analysis, including
    scaling, dimensionality reduction, kernel calculation, and biplots
    computation and display.

    Attributes
    ----------
    X:  pd.dataframe
        Input matrix of shape N x P.
    labels: array-like, optional
        Labels for the samples (default is None).
    perplexity: int or None, optional
        Perplexity for t-SNE (default is calculated as the square root of N).
    red: {'tsne', 'pca', 'umap'}, default is 'tsne'
        Dimensionality reduction method ('tsne' by default).
    sca: {'minmax'}, default is 'minmax'
        Data scaling method ('minmax' by default).
    random_seed: int, default is 123
        Seed for result reproducibility.

    Methods
    -------
    data_scaler(X, feature_range=(0, 1))
        Scale the data using MinMaxScaler if 'sca' is set to 'minmax'.
    reduce_dimensions(X)
        Reduce the dimensionality of the data using t-SNE, PCA, or UMAP.
    krbf(X)
        Calculate the Radial Basis Function (RBF) kernel matrix for the input data.
    center_kernel(K)
        Center a given kernel matrix using the Kernel Centering method.
    laplacian_score(X, K, tol=1e-10)
        Calculate the Laplacian score for a given dataset and kernel matrix.
    lnkbp_()
        Process and analyze the data through steps such as scaling, dimensionality reduction,
        kernel calculations, and Laplacian Score computation.
    localbp_(X_)
          Perform a local biplot operation on the scaled data (currently commented out).
    laplacian_score(X, K, tol=1e-10)
        Calculate the Laplacian score for a given dataset and kernel matrix
    GMD(X, H, Q, K)
        Generalized Matrix Decomposition method (power method) for a given dataset and kernel matrices.
    biplot_gmd_body(fit, index=None, names=None, sample_col='grey50', sample_pch=19, arrow_col='orange', arrow_cex=1)
        Generate a GMD-biplot based on generalized matrix decomposition results.
    plot_lnkbp_(hue, c, figsize=(25, 10))
        Plot various visualizations, including scatter plots, kernel matrices, and feature relevance.
    affine_transformM(parameters, array_A)
        Apply an affine transformation to the input array using the given parameters.
    registration_errorM(parameters, array_A, array_B)
        Compute the registration error between two sets of 2D points after applying an affine transformation.


    ...

    """
    def __init__(self, X, labels = None, perplexity = None, red = 'tsne', sca = 'minmax',random_seed=123):
          self.X = X.copy()
          self.columns_= self.X.columns
          self.labels = labels
          if perplexity==None:
            perplexity = round(np.sqrt(X.shape[0]))
          self.perplexity = perplexity
          self.random_seed = random_seed
          self.red = red
          self.sca = sca





    def data_scaler(self,X,feature_range=(0,1)):
        """
        this method scale the input data using MinMaxScaler if 'sca' is set to 'minmax'.

        Parameters
        ----------
        - X (array-like): Input matrix of shape N x P. Input data to be scaled.
        - feature_range (tuple, optional): Tuple specifying the minimum and maximum values of the feature range.
          Defaults to (0, 1).

        Returns
        ----------
        - An N x P scaled data matrix.
        """

        # Check if scaling method is 'minmax'
        if self.sca == 'minmax':
          # Create MinMaxScaler instance with specified feature_range
          sca_ = MinMaxScaler(feature_range=feature_range)
          # Fit and transform the data using the scaler
        return sca_.fit_transform(X)


    def reduce_dimensions(self, X):
        """
        Reduce the dimensionality of the input data using t-SNE, PCA, or UMAP.

        Parameters:
        ----------
        - X (array-like): Input matrix of shape N x P. Input data to be dimensionality reduced.

        Returns:
        ----------
        - An n x 2 array-like dimensionality reduced data.
        """

        # Choose the dimensionality reduction method
        if self.red == 'tsne':
          self.reduce_dimensions = TSNE(n_components = 2, perplexity = self.perplexity, random_state=self.random_seed)
        elif self.red == 'pca':
          self.reduce_dimensions = PCA(n_components = 2, random_state=self.random_seed)
        # Uncomment the following lines if you use UMAP
        # elif self.red == 'umap' :
        #   self.reduce_dimension = UMAP(n_components = 2, n_neighbors = round(np.sqrt(X.shape[0])),min_dist =0.9,random_state=self.random_seed)
        else:
          # Use t-SNE as a default if the specified method is not recognized
          self.reduce_dimensions = TSNE(n_components = 2, perplexity = self.perplexity, random_state=self.random_seed)
        # Return the dimensionality reduced data after scaling
        return self.data_scaler(self.reduce_dimensions.fit_transform(X))



    def krbf(self,X):
        """
        Calculate the Radial Basis Function (RBF) kernel matrix for the input data.

        Parameters:
        ----------
        - X : list | np.ndarray
              Input matrix of shape N x P.

        Returns:
        ----------
        - list | np.ndarray  N x N RBF kernel matrix.
        """
        # Calculate pairwise Euclidean distances between data points
        distance_matrix  = cdist(X,X)
        # Calculate the median of pairwise distances
        sigma_square = 0.5*np.median(squareform(distance_matrix))
        # Calculate the RBF kernel matrix using the median distance
        return np.exp(-distance_matrix**2/sigma_square)

    def center_kernel(self, K):

        """
        Center a given kernel matrix using the Kernel Centering method.

        Parameters:
        ----------
        - K: np.ndarray
             An N x N or P x P Input kernel matrix.

        Returns:
        ----------
        - np.ndarray: Centered kernel matrix.
        """
        # Get the number of samples
        n = K.shape[0]
        # Create a column vector of ones
        one_n = np.ones((n,1))
        # Calculate the centering matrix H
        H = np.eye(n) - (1 / n) * np.dot(one_n, one_n.T)
        # Center the kernel matrix using the Kernel Centering method and return it
        return (H.dot(K)).dot(H)



    #input features laplacian score
    def laplacian_score(self,X,K, tol=1e-10):
        """
        Calculate the Laplacian score for a given dataset and kernel matrix.

        Parameters:
        ----------
        - X: np.ndarray
             Input matrix of shape N x P.
        - K: np.ndarray
             Kernel matrix.
        - tolerance: float, optional
                     Tolerance value for numerical stability. Defaults to 1e-10.

        Returns:
        ----------
        - np.ndarray : Laplacian score for each data point.
        """
        # Calculate the diagonal matrix Dl of the kernel matrix
        Dl = np.diag(K.sum(axis=1)+tol)
        # Calculate the unnormalized Laplacian matrix L
        L = Dl - K # unnormalized
        #L = np.eye(Kk.shape[0])-np.diag((np.diag(Dl)**(-0.5))).dot(Kk).dot(np.diag((np.diag(Dl)**(-0.5))))
        # Center the data points
        X_ = X - np.kron(np.ones((1,Dl.shape[0])),((X.T).dot(Dl)).dot(np.ones((Dl.shape[0],1)))/(np.sum(np.diag(Dl)))).T
        # Calculate Laplacian score for each data point
        return np.diag((X_.T).dot(L).dot(X_))/np.diag((X_.T).dot(Dl).dot(X_))

    def LocalBiplot_(self):
        """
        Process and analyze the data using a series of steps, including scaling, dimensionality reduction,
        kernel calculations, and Laplacian score computation.

        Returns:
        ----------
        - YourClass instance: The modified instance with processed and analyzed data.
        """

        # Step 1: Scale the input data
        self.X_ = self.data_scaler(self.X) #scaler X
        # Step 2: Reduce dimensions using a chosen method
        self.Z = self.reduce_dimensions(self.X_) #red
        # Step 3: Perform a local biplot operation on the scaled data
        #self.localbp_(self.X_)
        # Step 4: Add the reduced dimensions to the original data
        self.X['P1'] = self.Z[:,0] #add red to pd
        self.X['P2'] = self.Z[:,1]
        # Step 5: Calculate kernel matrices for X scaled and Z
        self.KX = self.krbf(self.X_) #kernel X samples
        self.KXF = self.krbf(self.X_.T) #kernel X features
        self.KZ = self.krbf(self.Z) # kernel Z samples
        # Step 6: Calculate Laplacian scores for X and Z
        self.lsX = self.laplacian_score(self.X_,self.KX) #features KX
        self.lsZ = self.laplacian_score(self.X_,self.KZ) #features KZ

        return self

    #======================= funciones GMD ===========================================

    # Funcion get_uv_
    def get_uv(self, X, H, Q, u_0, v_0):#H N x N, Q P x P
        """

        GMD Algorithm (power method) for matrix factorization.

        Parameters:
        ----------
        - X (numpy.ndarray): Input matrix of shape N x P.
        - H (numpy.ndarray): Matrix H of shape (N, N).
        - Q (numpy.ndarray): Matrix Q of shape (P, P).
        - u_0 (numpy.ndarray): Initial vector u of shape (N,).
        - v_0 (numpy.ndarray): Initial vector v of shape (P,).

        Returns:
        ----------
        dict: A dictionary containing the following key-value pairs:
            - 'u' (numpy.ndarray): Matrix U of shape (N, K), where K is the number of iterations.
            - 'v' (numpy.ndarray): Matrix V of shape (P, K), where K is the number of iterations.

        Details:
        ----------

        GMD Algorithm (power method)
        1. Let $\mathbf{\check{X}}^{(1)} = \mathbf{X}$ and initialize $\mathbf{u}_1$ and $\mathbf{v}_1$

        2.  For $k= 1...K:$

        (a) Repeat until convergence:
        * set $\mathbf{u}_k = \frac{\mathbf{\check{X}}^{(k)}\mathbf{R}\mathbf{v}_k}{|| \mathbf{\check{X}}^{(k)}\mathbf{R}\mathbf{v}_k||_\mathbf{H}}$

        * set $\mathbf{v}_k = \frac{\mathbf{(\check{X}}^{(k)})^T\mathbf{H} \mathbf{u}_k}{|| \mathbf{\check{X}}^{(k)}\mathbf{H}\mathbf{u}_k||_\mathbf{R}}$

        (b) set $d_k = \mathbf{u}_k^T \mathbf{H}\mathbf{\check{X}}^{(k)}\mathbf{R}\mathbf{v}_k$

        (c) set $\mathbf{\check{X}}^{(k+1)} = \mathbf{\check{X}}^{(k)} -  \mathbf{u}_k d_k \mathbf{v}_k^T $

        3. Return $\mathbf{\tilde{U}} = [\mathbf{u_1,..., u_k}], \mathbf{\tilde{V}}= [\mathbf{v_1,..., v_k}], \mathbf{\tilde{S}} = diag(d_1,...d_k) $ .
        """

        u = X @ Q @ v_0 / (np.sqrt(v_0.T @ Q.T @ X.T @ H @ X @ Q @ v_0))
        v = X.T @ H @ u / (np.sqrt(u.T @ H.T @ X @ Q @ X.T @ H @ u))
        return {'u': u, 'v': v}


    # Funcion para hacer fit:
    def GMD(self, X, H, Q, K):
        """
        Generalized Matrix Decomposition method (power method)

        Computes the generalized matrix decomposition of X.

        The K-dimensional GMD of X with respect to H and Q is given by X = USV^T, where
        \deqn{(U, S, V) = argmin_{U,S,V} ||X - USV^T||^2_{H, Q},}
        subject to \eqn{U^THU = I_K, V^TQV = I_K} and \eqn{diag(S) \ge 0}. Here, for any N x P matrix A,
        ||A||^2_{H,Q} = tr(A^THAQ).

        Parameters:
        ----------
        - X An N x P data matrix.
        - H An N x N positive semi-definite similarity kernel.
        - Q An P x P positive semi-definite similarity kernel.
        - K a scalar specifying the dimension of GMD components (see Details).

        Returns:
        ----------
        A list of the GMD components U, S, V, H and Q (see Details).
        @author Parker Knight and Yue Wang \email{ywang2310@fredhutch.org}
        @references Allen, G. I., L. Grosenick, and J. Taylor (2014). A generalized least-square matrix decom- position. Journal of the American Statistical Association 109(505), 145–159.
        """


        error_vec = []
        n, p = X.shape
        # Output matrices/vectors
        U = np.zeros((n, K))
        V = np.zeros((p, K))
        D = np.zeros(K)
        X_0 = X
        u_0 = np.concatenate(([1], np.zeros(n-1)))
        v_0 = np.concatenate(([1], np.zeros(p-1)))
        for iter in range(1, K + 1):
            error = 1
            while error > 1e-14:
                temp_uv = self.get_uv(X_0, H, Q, u_0, v_0)
                u = temp_uv['u']
                v = temp_uv['v']
                error = np.linalg.norm(u - u_0, ord=2) + np.linalg.norm(v - v_0, ord=2)
                error_vec += [error]
                u_0 = u
                v_0 = v
            U[:, iter - 1] = u
            V[:, iter - 1] = v
            d = u.T @ H @ X_0 @ Q @ v
            D[iter - 1] = d
            X_0 = X_0 - (u[:, np.newaxis]*d)@v[np.newaxis, :]
        # plt.plot(error_vec)
        # plt.xlabel('iterations')
        # plt.ylabel('error grater than 1e-5')
        gmd_output = GMDOutput()
        gmd_output.U = U
        gmd_output.V = V
        gmd_output.D = D
        gmd_output.H = H
        gmd_output.Q = Q
        gmd_output.X = X
        return gmd_output


    def biplot_gmd_body(self, fit, index=None, names=None, sample_col='grey50', sample_pch=19, arrow_col='orange', arrow_cex=1):
        """

        The GMD-biplot
            Biplots based on generelized matrix decomposition.

            Parameters:
            ----------
            An object of class "gmd" that is the output from GMD method.
            ... Optional arguments (see Details).

            Details
            ----------
            The optional arguments that can be passed in the biplot are
            \itemize{

              \item index: a numeric vector specifying which variables(arrows) to display. The default is to plot the three longest arrows.}
              \item names:  a string vector specifying the names of the arrows. The default name of the i-th variable is Vi.
              \item sample_col: The color of the sample dots. The default is grey.
              \item sample_pch: Either an integer specifying a symbol or a single character to be used in plotting sample points. The default is 19.
              \item arrow_col: The color of the arrows. The default is orange.
              \item arrow_cex: A numeric value giving the size of the labels of the arrows. The default is 1.
              }

            @author Parker Knight and Yue Wang \email{ywang2310@fredhutch.org}
            @references Yue Wang, Timothy Randolph, Ali Shojaie and Jing Ma (2019). The GMD-biplot and its application to microbiome data.

            """
        U = fit.U
        D = fit.D
        V = fit.V
        U = U[:, np.argsort(D)[::-1]]
        V = V[:, np.argsort(D)[::-1]]
        k1 = np.argsort(D)[::-1][0]
        k2 = np.argsort(D)[::-1][1]
        D = np.sort(D)[::-1]
        eta = U @ np.diag(D)
        max_xlab = np.max(np.abs(eta[:, 0]))
        max_ylab = np.max(np.abs(eta[:, 1]))
        plt.figure(figsize=(8, 6))
        #plt.scatter(eta[:, 0], eta[:, 1],  c=sample_col)
        sns.scatterplot(x=eta[:, 0],
                    y= eta[:, 1],
                    hue =sample_col, palette = "viridis")
        plt.xlabel(f'PC{k1}', fontsize=16)
        plt.ylabel(f'PC{k2}', fontsize=16)
        plt.xlim(-1.1 * max_xlab, 1.1 * max_xlab+1)
        plt.ylim(-1.1 * max_ylab, 1.1 * max_ylab+1)
        # calculate coordinates

        Q = fit.Q
        V_plot = Q @ V
        arrow_x = V_plot[:, 0]
        arrow_y = V_plot[:, 1]
        max_xarrow = np.max(np.abs(arrow_x))
        max_yarrow = np.max(np.abs(arrow_y))
        xratio = max_xarrow / max_xlab
        yratio = max_yarrow / max_ylab

        xaxp = np.linspace(-max_xlab, max_xlab, num=5)
        yaxp = np.linspace(-max_ylab, max_ylab, num=5)

        xlab_arrow = xaxp * xratio
        ylab_arrow = yaxp * yratio
        print(f"len of V = {len(V)}")
        print(f"len of x arrow = {len(arrow_x)}")
        print(f"len of y arrow = {len(arrow_y)}")
        print(f"len of names = {len(names)}")
        iter = 0
        for i in index:

            #arrow_length = np.sqrt(arrow_x[i] ** 2 + arrow_y[i] ** 2)
            #if arrow_length >= 0.1:
            plt.arrow(0, 0, arrow_x[i] / xratio, arrow_y[i] / yratio, head_width=0.1, head_length=0.1,  color=arrow_col)
            if names is not None:
            # print(f"i = {i}")
              plt.text(arrow_x[i]/ xratio, arrow_y[i] / yratio * 1.06, names[iter], fontsize=17, color='black')
              iter += 1

        # Add new axes
        plt.xticks(xaxp, labels=[f'{round(val, 2)}' for val in xlab_arrow], fontsize=16)
        plt.yticks(yaxp, labels=[f'{round(val, 2)}' for val in ylab_arrow], fontsize=16)
        plt.gca().tick_params(axis='both', which='both', length=0)
        plt.legend(loc='upper left', title= sample_col.name)
        plt.legend(fontsize=16)
        #plt.colorbar()

        plt.show()

    #===================== Fin funciones GMD ============================================


    def plot_lnkbp_(self,hue, c, figsize = (25,10)):
        """
        Plot various visualizations for Kernel Biplots (KBP) and Laplacian Score (LS).

        Parameters:
        ----------
        - hue: str
            Variable to use for coloring in scatter plots.
        - c: str
            Variable to use for coloring in the scatter plot.
        - figsize: tuple, optional
            Figure size (default is (25, 10)).

        Returns:
        ----------
        None

        Plots:
        ----------
        - Subplot 1: Scatter plot with Kernel Density Estimate (KDE).
        - Subplot 2: Scatter plot with local biplot markers.
        - Subplot 3: Kernel matrix for samples (KX).
        - Subplot 4: Kernel matrix for reduced dimensions (KZ).
        - Subplot 5: Kernel matrix for input features (KXF).
        - Subplot 6: Bar plot showing Laplacian Scores for Z (LS_Z) and X (LS_X).

        """
        fig, ax = plt.subplots(2,3,figsize=figsize)

        # Scatter plot with Kernel Density Estimate (KDE)
        kdeplot(data=self.X, x='P1', y='P2',hue=hue, ax=ax[1,0], levels=3)
        self.X.plot(kind='scatter',x='P1',y='P2',ax=ax[1,0],c=c,cmap='jet',legend=False)

        # Scatter plot with local biplot markers
        cmap_ = matplotlib.cm.jet(np.linspace(0,1,len(self.C)))
        for c,vc in enumerate(self.C):
            ax[1,1].scatter(self.muZ[c,0],self.muZ[c,1],marker='d',s=100,c=cmap_[c])
            ax[1,1].scatter(self.lpca[c][:,0],self.lpca[c][:,1],c=cmap_[c])

        # Kernel matrices for samples (KX), reduced dimensions (KZ), and input features (KXF)
        vmin = min(self.KX.ravel().min(),self.KZ.ravel().min(),self.KXF.ravel().min() )
        vmax = max(self.KX.ravel().max(),self.KZ.ravel().max(),self.KXF.ravel().max() )
        ax[0,0].imshow(self.KX,vmin=vmin,vmax=vmax, cmap='Reds')
        ax[0,0].set_xlabel('Samples')
        ax[0,0].set_ylabel('Samples')
        ax[0,1].imshow(self.KZ,vmin=vmin,vmax=vmax, cmap='Reds')
        ax[0,1].set_xlabel('Samples')
        ax[0,1].set_ylabel('Samples')


        im_ = ax[0,2].imshow(self.KXF,vmin=vmin,vmax=vmax, cmap='Reds')
        ax[0,2].set_xlabel('Features')
        ax[0,2].set_ylabel('Features')
        # Colorbar for kernel matrices
        cax = fig.add_axes([0.92, 0.5, 0.01, 0.4])
        norm = matplotlib.colors.Normalize(vmin=vmin,vmax=vmax)
        sm = plt.cm.ScalarMappable(cmap='Reds', norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm,cax=cax)

        #feature relevance  showing Laplacian Scores for Z (LsZ) and X (lsX)
        ax[1,2].bar(np.arange(len(self.lsZ)),self.lsZ,label='LS_Z')#red kernel
        ax[1,2].bar(np.arange(len(self.lsX)),self.lsX,bottom=self.lsZ,label='LS_X')#input kernel

        ax[1,2].set_xticks(ticks=np.arange(len(self.lsX)),labels=self.columns_,rotation=90)
        ax[1,2].legend()
        ax[1,2].set_ylabel('Laplacian Score')
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        #plt.tight_layout()
        plt.show()



    def plot_transformed_clusters(self, ax, ZcA, VA, cmap,  arrow_size = 0.05 ):
        """
        Plot the non-linear local-Biplot SVD.

        Parameters:
        ----------
        - ax (matplotlib.axes._subplots.AxesSubplot): Axes on which to plot.
        - ZcA (numpy.ndarray): Transformed points of the cluster.
        - VA (numpy.ndarray): Transformed vector arrows of the cluster.
        - cmap: Color map for the scatter plot.
        - arrow_size

        Returns:
        ----------
        None
        """

        texts = []
        # Calculate mean of transformed points
        ZcA_mean = ZcA.mean(axis=0)



        # Set arrow size and color



        # Scatter plot of transformed points
        ax.scatter(ZcA[:, 0], ZcA[:, 1], alpha=0.7, c=cmap)

        # Extract arrow coordinates from transformed vector arrows
        VA = VA /np.linalg.norm(VA,axis=0)

        arrow_x = VA[:, 0]
        arrow_y = VA[:, 1]

        # Calculate maximum values for scaling
        max_xlab = np.max(np.abs(ZcA[:, 0]))
        max_ylab = np.max(np.abs(ZcA[:, 1]))
        max_xarrow = np.max(np.abs(arrow_x))
        max_yarrow = np.max(np.abs(arrow_y))
        xratio = max_xarrow / max_xlab
        yratio = max_yarrow / max_ylab

        # Set axis points for arrow scaling
        xaxp = np.linspace(-max_xlab, max_xlab, num=5)
        yaxp = np.linspace(-max_ylab, max_ylab, num=5)

        xlab_arrow = xaxp * xratio
        ylab_arrow = yaxp * yratio

        # Calculate mean of transformed points for arrow origin
        ZcA_mean = ZcA.mean(axis=0)

        # Plot vector arrows and labels
        for k in range(VA.shape[0]):
            ax.arrow(ZcA_mean[0], ZcA_mean[1], (arrow_x[k] / xratio)*0.5, (arrow_y[k] / yratio)*0.5,
                     head_width= arrow_size, head_length= arrow_size, color='gray', linewidth=1.1)
            # ax.text(((arrow_x[k]) / xratio)*0.5 + ZcA_mean[0] + 0.05, (arrow_y[k] / yratio)*0.5 + ZcA_mean[1],
            #         s='f' + str(k + 1), fontsize=16, color='black')
            ax.text(((arrow_x[k]) / xratio)*0.5 + 0.03 + ZcA_mean[0], (arrow_y[k] / yratio)*0.5 + ZcA_mean[1]+ 0.01,
                     s='f' + str(k + 1), fontsize=16, color='black') #, fontsize=15

        #adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
        #ax.set_xlim((-1,1))
        ax.set_ylim((-1,1.4))
        # Set plot title and axis labels
       # ax.set_title('Non-linear local-biplot SVD', fontsize=20)
        ax.set_xlabel('Dimension 1', fontsize=20)
        #ax.set_ylabel('PC 2', fontsize=20)
        ax.tick_params(axis='both', labelsize=20)
        #ax.set_yticks([])
        # Remove the upper and right spines
        #ax.spines['top'].set_visible(False)
        #ax.spines['right'].set_visible(False)

        # Display grid
        #ax.grid(True)



    def affine_transformM(self, parameters, array_A):
        """
          Apply an affine transformation to the input array using the given parameters.

          Parameters:
          ----------
          - parameters (array-like): Affine transformation parameters.
              - parameters[0]: Scaling factor
              - parameters[1]: Rotation angle (in radians)
              - parameters[2:]: Translation along x and y axes
          - array_A (array-like): Input array to be transformed.

          Returns:
          ----------
          - array-like: Transformed array after applying the affine transformation.

          """
        # Apply affine transformation to array_A with parameters
        N = array_A.shape[0] #N x 2 array
        scale = parameters[0]
        rotation = parameters[1]
        translation = parameters[2:]
        transformation_matrix = np.array([
            [scale * np.cos(rotation), -scale * np.sin(rotation), translation[0]],
            [scale * np.sin(rotation), scale * np.cos(rotation), translation[1]],
        ]) # 2 x 3 transformation matrix
        transformed_A = np.dot(transformation_matrix, np.c_[array_A,np.ones((N,1))].T)
        return transformed_A.T

    def registration_errorM(self, parameters, array_A, array_B): # N x 2 arrays
        """
        Compute the registration error between two sets of 2D points after applying an affine transformation.

        Parameters:
        ----------

        - parameters (array-like): Affine transformation parameters.
        - array_A (array-like): Source set of 2D points (N x 2 array).
        - array_B (array-like): Target set of 2D points (N x 2 array).

        Returns:
        ----------

        - float: Registration error, calculated as the Frobenius norm of the difference
                between the transformed source points and the target points.
        """
        # Compute the registration error (sum of squared differences)
        transformed_A = self.affine_transformM(parameters, array_A)
        N = array_A.shape[0]
        error = (1/N)*np.linalg.norm(transformed_A - array_B,'fro')
        return error



    def optimize_affine_transform(self, Zc, B, Sc, ind_):
        """
        Optimize the parameters for the affine transformation.

        Parameters:
        ----------
        - Zc (array-like): Cluster data points (N x 2 array).
        - B (array-like): Matrix of vectors (2 x P) representing the original basis.
        - Sc (array-like): Singular values of the original basis.
        - ind_ (array-like): Boolean array indicating the indices of the cluster.

        Returns:
        ----------
        - Tuple: A tuple containing the optimized parameters and the transformed cluster points.

        Notes:
        ----------
        This function performs optimization to find the best affine transformation parameters
        using the Nelder-Mead method. It then applies the optimized transformation to the cluster points.
        """
        # Initial guess for optimization parameters (scale, rotation, translation)
        initial_parameters = np.array([1.0, 0.0, 0.0, 0.0])

        # Perform the optimization to find the best affine transformation
        result = minimize(self.registration_errorM, initial_parameters,
                          args=(Zc, self.Z[ind_]), method='Nelder-Mead')

        # Get the optimized parameters
        optimized_parameters = result.x

        # Apply the optimized transformation to the cluster points and vectors
        Zc_transformed = self.affine_transformM(optimized_parameters, Zc)
        B_transformed = self.affine_transformM(optimized_parameters, B)



        return optimized_parameters, Zc_transformed, B_transformed


    def clustering(self, Z, eps_=None, per_=5): #N x 2 array
        """
        Perform clustering on the given 2D data using DBSCAN algorithm.

        Parameters:
        ----------
        - Z (array-like): N x 2 list | np.ndarray  representing the data points.
        - eps_ (float, optional): The maximum distance between two samples for one to be considered
          as in the neighborhood of the other. Defaults to None.
        - per_ (float, optional): The percentile value used to set the `eps` parameter if it is not provided.
          Defaults to 5.

        Returns:
        ----------
        - list | np.ndarray : An array of cluster labels assigned by the DBSCAN algorithm.

        Notes:
        ----------
        If `eps_` is not provided, it is calculated as a percentile of the pairwise Euclidean distances
        between points in the input data `Z`.

        DBSCAN (Density-Based Spatial Clustering of Applications with Noise) is a clustering algorithm
        that groups together data points that are close to each other and marks outliers as noise.

        """
        if eps_ == None:
          eps_=np.percentile(squareform(cdist(Z, Z)),q=per_)
        np.random.seed(123)
        clus = DBSCAN(eps=eps_)
        clus.fit(Z)
        return clus.labels_

    def pca_by_SVD(self, X):
        """
        Perform SVD decomposition.

        Parameters:
        ----------
        - X: list | np.ndarray
          Input data N x P.

        Returns:
        ----------

        -  U, S, VT, S_, A, B

        Details:
        ----------

        Singular Value Decomposition

        (utilizar ..math:: en lugar de $$)
        $\mathbf{X} = \mathbf{U}\mathbf{S}\mathbf{V}^\top = \mathbf{U}\mathbf{S}^{0.5}\mathbf{S}^{0.5}\mathbf{V}^\top = \mathbf{A}\mathbf{B}^\top$

        $\mathbf{X}\in \mathbb{R}^{N \times P}$

        $\mathbf{U}\in \mathbb{R}^{N \times M}$

        $\mathbf{V}\in \mathbb{R}^{P \times M}$

        $\mathbf{S}\in \mathbb{R}^{M \times M}$

        $\mathbf{A} =  \mathbf{U}\mathbf{S}^{0.5} \in \mathbb{R}^{N \times M} $

        $\mathbf{B} = \mathbf{V}\mathbf{S}^{0.5} \in \mathbb{R}^{P \times M} $

        $M = min(N,P)$
        """
        #centering data
        X -= X.mean()



        # SVD decomposition

        U, S, VT = np.linalg.svd(X)

        # Use the full set of singular values
        S_ = S
        A = U[:, :S_.shape[0]].dot((np.diag(S_))**(0.5))  # samples-based basis
        B = VT.T[:, :S_.shape[0]].dot((np.diag(S_))**(0.5)) # features-based basis


        Zc = X.dot(VT.T[:,:2]) # x x V^T


        # PCA projection from SVD -> without standard scaler or min-max scaler


        return U, S, VT, S_, A, B, Zc

    def plot_correlation_matrix(self, ax, data, title, color='black', fontsize = 12):
        """
        Plot a correlation matrix subplot.

        Parameters:
        ----------
        - ax (matplotlib.axes._subplots.AxesSubplot): Axes for the subplot.
        - data (numpy.ndarray): Data for the correlation matrix.
        - title (str): Title for the subplot.
        - color: Color for the title.

        Returns:
        ----------
        None
        """
        im = ax.imshow(data, cmap='viridis')
        # ax.set_title(title, color=color, fontsize=fontsize)
        # ax.set_xlabel('Index', fontsize=fontsize)
        # ax.set_ylabel('Index', fontsize=fontsize)
        # im.set_clim(-1, 1)


        return im


        return

if __name__ == "__main__":
    rice_ = LocalBiplot(databp,labels= None,perplexity=None,red = 'tsne') #class instance
    rice_.LocalBiplot_()
