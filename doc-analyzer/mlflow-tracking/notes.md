## 14 mai
Il y a un problème avec le security context

Voir : https://github.com/cert-manager/cert-manager/issues/5516

Mais je n'ai pas résolu le problème.
Pour le momement j'ai tenté
- de commenter dans values.yaml toutes les occurences des valeurs suivantes:
```yml
    seccompProfile:
       type: "RuntimeDefault"
```
- de passer à `false` toutes les occurences de `containerSecurityContext.enabled`
- de commenter toute les occurences de la section `containerSecurityContext`
- de passer en plus toutes les occurences de `podSecurityContext.enabled` à false

Au soir du 14 mai, rien n'y fait. 


## 16 mai
Ensuite j'ai essayé avec une ancienne version du chart, rien n'y fait.

J'ai voulu tester sur minikube, mais l'installation ne fonctionne pas pour le moment, un problème de plus. Il s'avère que MacOs n'autorise plus les adaptateurs réseau virtuels 'host only'.
Heuresement, le docker engine Orbstack a une option Kubernetes qui fonctionne. OUF !

Donc l'installation de mlflow tracking va-t-elle fonctionner localement sur ma machine ? suspens intenable...

Réponse ... NON ça ne fonctionne pas. Quid faciam ? Nescio.

Retentative sur le cluster heia, avec values.yml par défaut, puis securityContext à false, puis seccompProfile.type à "", puis mise en commentaire de seccompProfile. Toujours la même erreur

retentative en désactivant minio et postgres, sachant que ça limitera les fonctionnalités, et ça fonctionne, avec un mais : pas d'accès exerne, le service loadbalancer reste en état pending.

retentative avec `clusterDomain: kube.isc.heia-fr.ch`, mais toujours ` Service is ready:Load balancer is being provisioned `.

retentative avec `service.type: ClusterIP`, `ingress.enabled: true` et `ingress.hostname: mlflow.kube.isc.heia-fr.ch`.