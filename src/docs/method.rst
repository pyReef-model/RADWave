What is the LEC?
================

**LEC** quantifies the closeness of a site to all others with **similar elevation**.
For a given landscape, LEC is primarily dependent on **elevation range** and on **species niche width**. It quantifies the closeness of any point in the landscape to all others at similar elevation.

It has been shown that **LEC** captures well the :math:`\alpha`-**diversity variations** observed in mountainous landscape [Lomolino2008]_ and simulated by full **meta-community models** [Bertuzzo2016]_ as shown in the figure below.

.. image:: ../RADWave/Notebooks/images/pearson.jpg
   :scale: 20 %
   :alt: LEC versus diversity
   :align: center

.. important::
  It suggests that **geomorphic features** are a **first-order control on biodiversity** and that **LEC** metric can be used to  quickly assess **species richness distribution in complex landscapes**.


Cost function
-------------

Considering a 2D lattice made of *N* squared cells, LEC for cell *i* (:math:`{LEC}_i`) is given by

.. math::
   {LEC}_i = \sum_{j=1}^N C_{ji}

where :math:`C_{ji}` quantifies the closeness between sites *j* and *i* with respect to elevational connectivity. :math:`C_{ji}` measures the cost for a given species adapted to cell *j* to spread and colonise cell *i*. This cost is a function of **elevation** and evaluates how often species adapted to the elevation of cell *j* have to **travel outside their optimal species niche width** (:math:`\sigma`) to reach cell *i* (as shown in the figure below).

Following Bertuzzo et al. [Bertuzzo2016]_, :math:`C_{ji}` is expressed as:

.. math::
   -\ln C_{ji} = \frac{1}{2\sigma^2} \min_{p  \in \{j\rightarrow i\}} \sum_{r=2}^L (z_{k_r}-z_j)^2

where :math:`p=[k_1,k_2, ...,k_L]` (with :math:`k_1=j` and :math:`k_L=i`) are the cells comprised in the path *p* from *j* to *i*.

.. image:: ../RADWave/Notebooks/images/path.jpg
   :scale: 20 %
   :alt: LEC computation
   :align: center

In the figure above, we illustrate the approach implemented in **RADWave** to compute the closeness measure (:math:`C_{ji}`) used to quantify **LEC** based on a topography grid (adapted from [Bertuzzo2016]_). Two paths from site *j* to *i* (inset) are proposed with their elevation profiles. Associated costs are computed following the equation above (:math:`\sum_{r=2}^L (z_{k_r}-z_j)^2`).


.. hint::
    Despite a longer length, **the cost associated to the red path is smaller than that of the blue one** as it passes across sites with similar elevations to :math:`z_j`.

`Dijkstra's algorithm`_
-----------------------

The estimation of :math:`C_{ji}` requires computation of **all the possible paths** *p* from *j* to *i* and is defined as the maximum closeness value along these paths and this is solved for each cell *j* using **Dijkstra's algorithm** [Dijkstra1959]_ with diagonal connectivity between cells.

For each cell *j*, the algorithm  builds a **Dijkstra tree** that branches the given cell with all the cells defining the simulated region. **Edge weights** are set equal to the square of the difference between the considered vertex elevation (:math:`z_{k_r}`) and :math:`z_j`. The least-cost distance between *j* and *i* is then calculated as the **minimum sum of edge weights** obtained from the cells along the shortest-path (see top figure).

Here, the closeness is measured as a **least-cost** distances that optimises the costs associated to the edge weights of the traversed cells as well as the travelled Euclidean distance. As the least-cost distances incorporate landscape costs to movement, the approach allows for **closeness differentiation** between cells that might be seen as *equally near* if landscape costs were not accounted for.

In **bioLEC** we rely on `scikit-image`_ to compute the least cost distances [Etherington2017]_. `scikit-image`_ package is primarily intended to process image [vanderWalt2014]_ but is designed to work with **NumPy arrays** making it compatible with other Python packages (*e.g.* most other geospatial Python packages) and really simple to use with digital elevation datasets.

While `scikit-image`_ uses slightly different terminology, talking about **minimum cost paths** rather than **least-cost paths**, the approach is identical to those commonly implemented in GIS software and applies Dijkstra's algorithm with diagonal connectivity between cells [Etherington2016]_.


Parallelisation
---------------

**Dijkstra’s algorithm** is a graph search algorithm that solves single-source shortest path for a graph with non-negative weights. Such an algorithm can be quite long to solve especially in **bioLEC** as it needs to be used to compute the **least-cost paths** for every points on the surface.

.. image:: ../RADWave/Notebooks/images/parallel.jpg
   :scale: 50 %
   :alt: Parallel runtime
   :align: center

Here we do not perform a parallelisation of the **Dijkstra’s algorithm** but instead we adopt a simpler strategy where the **Dijkstra trees** for all paths are balanced and distributed over multiple processors using message passing interface (**MPI**). The approach consists in splitting the computational domain row-wise as shown in the above figure.  **Least-cost paths** are then computed for the points belonging to each sub-domain using the **Dijkstra’s algorithm** over the entire region.

.. note::
  Using this approach, LEC computation is significantly reduced and **scales really well with increasing CPUs**.

.. [Bertuzzo2016] E. Bertuzzo, F. Carrara, L. Mari, F. Altermatt, I. Rodriguez-Iturbe & A. Rinaldo -
  Geomorphic controls on species richness. PNAS, 113(7) 1737-1742, `DOI: 10.1073/pnas.1518922113`_, 2016.

.. [Dijkstra1959] E.W. Dijkstra -
  A note on two problems in connexion with graphs. Numer. Math. 1, 269-271, `DOI: 10.1007/BF01386390`_, 1959.

.. [Etherington2016] T.R. Etherington -
  Least-cost modelling and landscape ecology: concepts, applications, and opportunities. Current Landscape Ecology Reports 1:40-53, `DOI: 10.1007/s40823-016-0006-9`_, 2016.

.. [Etherington2017] T.R. Etherington -
  Least-cost modelling with Python using scikit-image, Blog_, 2017.

.. [Lomolino2008] M.V. Lomolino -
  Elevation gradients of species-density: historical and prospective views. Glob. Ecol. Biogeogr. 10, 3-13, `DOI: 10.1046/j.1466-822x.2001.00229.x`_, 2008.

.. [vanderWalt2014] S. van der Walt, J.L. Schönberger, J. Nunez-Iglesias, F. Boulogne, J.D. Warner, N. Yager, E. Gouillart & T. Yu -
  Scikit Image Contributors - scikit-image: image processing in Python, `PeerJ 2:e453`_, 2014.



.. _`DOI: 10.1073/pnas.1518922113`: http://www.pnas.org/cgi/doi/10.1073/pnas.1518922113
.. _`DOI: 10.1007/BF01386390`: https://link.springer.com/article/10.1007/BF01386390
.. _`DOI: 10.1007/s40823-016-0006-9`: https://link.springer.com/article/10.1007/s40823-016-0006-9
.. _Blog: http://tretherington.blogspot.com/2017/01/least-cost-modelling-with-python-using.html
.. _`DOI: 10.1046/j.1466-822x.2001.00229.x`: https://doi.org/10.1046/j.1466-822x.2001.00229.x
.. _`PeerJ 2:e453`: https://peerj.com/articles/453/
.. _`scikit-image`: http://scikit-image.org/
.. _`Dijkstra's algorithm`: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
