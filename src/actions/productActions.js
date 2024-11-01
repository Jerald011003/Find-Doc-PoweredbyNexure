import {
    PRODUCT_LIST_REQUEST,
    PRODUCT_LIST_SUCCESS,
    PRODUCT_LIST_FAIL,
    PRODUCT_DETAILS_REQUEST,
    PRODUCT_DETAILS_SUCCESS,
    PRODUCT_DETAILS_FAIL,
    PRODUCT_DELETE_REQUEST,
    PRODUCT_DELETE_SUCCESS,
    PRODUCT_DELETE_FAIL,
    PRODUCT_CREATE_REQUEST,
    PRODUCT_CREATE_SUCCESS,
    PRODUCT_CREATE_FAIL,
    PRODUCT_UPDATE_REQUEST,
    PRODUCT_UPDATE_SUCCESS,
    PRODUCT_UPDATE_FAIL,
    PRODUCT_CREATE_REVIEW_REQUEST,
    PRODUCT_CREATE_REVIEW_SUCCESS,
    PRODUCT_CREATE_REVIEW_FAIL,
    PRODUCT_TOP_REQUEST,
    PRODUCT_TOP_SUCCESS,
    PRODUCT_TOP_FAIL,
} from '../constants/productConstants';

import axiosInstance from '../actions/axiosInstance';

export const listProducts = (keyword = '') => async (dispatch) => {
    try {
        dispatch({ type: PRODUCT_LIST_REQUEST });

        const { data } = await axiosInstance.get(`/api/products${keyword}`);

        dispatch({
            type: PRODUCT_LIST_SUCCESS,
            payload: data,
        });
    } catch (error) {
        dispatch({
            type: PRODUCT_LIST_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};

export const listTopProducts = () => async (dispatch) => {
    try {
        dispatch({ type: PRODUCT_TOP_REQUEST });

        const { data } = await axiosInstance.get(`/api/products/top/`);

        dispatch({
            type: PRODUCT_TOP_SUCCESS,
            payload: data,
        });
    } catch (error) {
        dispatch({
            type: PRODUCT_TOP_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};

export const listProductDetails = (id) => async (dispatch) => {
    try {
        dispatch({ type: PRODUCT_DETAILS_REQUEST });

        const { data } = await axiosInstance.get(`/api/products/${id}`);

        dispatch({
            type: PRODUCT_DETAILS_SUCCESS,
            payload: data,
        });
    } catch (error) {
        dispatch({
            type: PRODUCT_DETAILS_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};

export const deleteProduct = (id) => async (dispatch, getState) => {
    try {
        dispatch({ type: PRODUCT_DELETE_REQUEST });

        const {
            userLogin: { userInfo },
        } = getState();

        await axiosInstance.delete(`/api/products/delete/${id}/`, {
            headers: {
                Authorization: `Bearer ${userInfo.token}`,
            },
        });

        dispatch({ type: PRODUCT_DELETE_SUCCESS });
    } catch (error) {
        dispatch({
            type: PRODUCT_DELETE_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};

export const createProduct = () => async (dispatch, getState) => {
    try {
        dispatch({ type: PRODUCT_CREATE_REQUEST });

        const {
            userLogin: { userInfo },
        } = getState();

        const { data } = await axiosInstance.post(`/api/products/create/`, {}, {
            headers: {
                Authorization: `Bearer ${userInfo.token}`,
            },
        });

        dispatch({
            type: PRODUCT_CREATE_SUCCESS,
            payload: data,
        });
    } catch (error) {
        dispatch({
            type: PRODUCT_CREATE_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};

export const updateProduct = (product) => async (dispatch, getState) => {
    try {
        dispatch({ type: PRODUCT_UPDATE_REQUEST });

        const {
            userLogin: { userInfo },
        } = getState();

        const { data } = await axiosInstance.put(
            `/api/products/update/${product._id}/`,
            product,
            {
                headers: {
                    Authorization: `Bearer ${userInfo.token}`,
                },
            }
        );

        dispatch({
            type: PRODUCT_UPDATE_SUCCESS,
            payload: data,
        });

        dispatch({
            type: PRODUCT_DETAILS_SUCCESS,
            payload: data,
        });
    } catch (error) {
        dispatch({
            type: PRODUCT_UPDATE_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};

export const createProductReview = (productId, review) => async (dispatch, getState) => {
    try {
        dispatch({ type: PRODUCT_CREATE_REVIEW_REQUEST });

        const {
            userLogin: { userInfo },
        } = getState();

        const { data } = await axiosInstance.post(
            `/api/products/${productId}/reviews/`,
            review,
            {
                headers: {
                    Authorization: `Bearer ${userInfo.token}`,
                },
            }
        );

        dispatch({
            type: PRODUCT_CREATE_REVIEW_SUCCESS,
            payload: data,
        });
    } catch (error) {
        dispatch({
            type: PRODUCT_CREATE_REVIEW_FAIL,
            payload: error.response && error.response.data.detail
                ? error.response.data.detail
                : error.message,
        });
    }
};
