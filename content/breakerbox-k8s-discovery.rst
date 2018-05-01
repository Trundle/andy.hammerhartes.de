========================================
Dropwizard + Tenacity + k8s + Breakerbox
========================================

:date: 2018-05-01 21:23
:tags: en, k8s, dropwizard, tenacity

Today's post sketches out how one can make `Breakerbox`_ discover `Dropwizard`_
service instances inside a `k8s`_ cluster. `Breakerbox`_ is a dashboard and
dynamic configuration tool for `Tenacity`_. If you have never heard of
Dropwizard or Tenacity or if you don't use Kubernetes, this post is probably
very boring to you.

The first step is to instruct breakerbox to use k8s for instance discovery. This
can be done by adding the following to your breakerbox YAML configuration file:

.. code:: yaml

   instanceDiscoveryClass: com.yammer.breakerbox.turbine.KubernetesInstanceDiscovery

Breakerbox's k8s instance discovery only discovers pods that are annotated with
``breakerbox-port``. Which makes some sense, considering that not all your
services might be using Dropwizard or that they might expose multiple ports.
Hence in the specs of your Dropwizard service pods, add:

.. code:: yaml

   metadata:
     annotations:
       breakerbox-port: "8080"

Note the quotes around the port, as k8s only allows string values for
annotations.

If you have `role-based access control
<https://kubernetes.io/docs/admin/authorization/rbac/>`_ in place in your k8s
cluster, you might also want to add a *breakerbox* cluster role that contains
all the permissions required to do the instance discovery. Only one permission
is required and that is listing the pods:

.. code:: yaml

   kind: ClusterRole
   apiVersion: rbac.authorization.k8s.io/v1
   metadata:
     name: breakerbox
   rules:
   - apiGroups: [""]
     resources: ["pods"]
     verbs: ["list"]

Don't forget to add a corresponding ``ClusterRoleBinding`` as well, with a
service account as subject. Then use the same service account in the pod spec of
your breakerbox service.

In case something doesn't work, don't be afraid to look into the `source of the
k8s instance discovery
<https://github.com/yammer/breakerbox/blob/ac6960bf28509fb04198409bdae9b97c0e29e260/breakerbox-turbine/src/main/java/com/yammer/breakerbox/turbine/KubernetesInstanceDiscovery.java>`_.
At the time of writing, it consists of merely 77 lines of code.

.. _Breakerbox: https://github.com/yammer/breakerbox
.. _Dropwizard: http://www.dropwizard.io/
.. _k8s: https://kubernetes.io/
.. _Tenacity: https://github.com/yammer/tenacity
