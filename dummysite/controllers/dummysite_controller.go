/*


Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package controllers

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"github.com/go-logr/logr"
	core "k8s.io/api/core/v1"
	metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
	"k8s.io/apimachinery/pkg/runtime"
	"math"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"

	stabledwkv1 "stable.dwk/api/v1"
)

// DummysiteReconciler reconciles a Dummysite object
type DummysiteReconciler struct {
	client.Client
	Log    logr.Logger
	Scheme *runtime.Scheme
}

func randomBase16String(l int) string {
	buff := make([]byte, int(math.Round(float64(l)/2)))
	rand.Read(buff)
	str := hex.EncodeToString(buff)
	return str[:l] // strip 1 extra character we get from odd length results
}

func constructPodForDummysite(dummysite *stabledwkv1.Dummysite, url string) *core.Pod {

	return &core.Pod{
		ObjectMeta: metav1.ObjectMeta{
			Name:      dummysite.Name,
			Namespace: dummysite.Namespace,
			Labels: map[string]string{
				"app": dummysite.Name,
			},
		},
		Spec: core.PodSpec{
			Containers: []core.Container{
				{
					Name:  dummysite.Name,
					Image: "kriegmachine/dsfetcher",
					Args:  []string{dummysite.Spec.WebsiteUrl},
				},
			},
		},
	}
}

// +kubebuilder:rbac:groups=stable.dwk.stable.dwk,resources=dummysites,verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups=stable.dwk.stable.dwk,resources=dummysites/status,verbs=get;update;patch

func (r *DummysiteReconciler) Reconcile(req ctrl.Request) (ctrl.Result, error) {
	ctx := context.Background()
	_ = r.Log.WithValues("dummysite", req.NamespacedName)

	var dummysite stabledwkv1.Dummysite

	if err := r.Get(ctx, req.NamespacedName, &dummysite); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}

	dep := constructPodForDummysite(&dummysite, dummysite.Spec.WebsiteUrl)

	if err := r.Create(ctx, dep); err != nil {
		fmt.Println(err, "Unable to create a pod")
		return ctrl.Result{}, err
	}

	fmt.Println("Created a pod for Dummysite:" + dummysite.Spec.WebsiteUrl)
	return ctrl.Result{}, nil
}

func (r *DummysiteReconciler) SetupWithManager(mgr ctrl.Manager) error {
	return ctrl.NewControllerManagedBy(mgr).
		For(&stabledwkv1.Dummysite{}).
		Complete(r)
}
