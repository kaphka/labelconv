(ns ocr-site.core
  (:require [om.core :as om]
            [om.dom :as dom]
            [ajax.core :refer [GET POST]]))

(enable-console-print!)
(def ENTER_KEY 13)

(println "Editsto this text should show up in your developer console.")

;; define your app data so that it doesn't get over-written on reload

(defonce app-state (atom {:data [] :current [] }))
(defonce files (atom {:text "Hi"}))

(defn error-handler [{:keys [status status-text]}]
  (print (str "something bad happened: " status " " status-text)))

(defn handler [response]
  (assoc! @app-state :data response)
  (print "got files " (:items response))
  (map #(print (str %)) (:items response)))

(GET "/data" {:response-format :json
            :handler handler
            :keywords? true
            :error-handler error-handler})

(defn widget [data owner]
  (reify
    om/IRender
    (render [this]
      (dom/p nil (:text data)))))
(om/root widget @app-state
  {:target (. js/document (getElementById "app"))})

(defn files-view [files owner]
  (reify
    om/IRender
    (render [this]
      (apply dom/ul nil
        (map (fn [name] (dom/li nil name)) (:items files))))))

(om/root files-view @files
  {:target (. js/document (getElementById "app"))})

(defn on-js-reload []
  ;; optionally touch your app-state to force rerendering depending on
  ;; your application
  ;;(swap! app-state update-in [:__figwheel_counter] inc)
)
