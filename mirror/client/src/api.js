
const api = {
    GET_MODULE : '/api/model',
    GET_VISUALISATIONS: '/api/visualisation',
    PUT_VISUALISATIONS: '/api/visualisation',
    getModuleLayerOutput : (id) => `/api/model/layer/output/${id}`
}

export default api