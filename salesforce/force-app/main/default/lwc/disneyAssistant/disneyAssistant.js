import { LightningElement, track } from 'lwc';

import chat from
    '@salesforce/apex/DisneyAgentController.chat';

import getTrace from
    '@salesforce/apex/DisneyAgentController.getTrace';

import getMetrics from
    '@salesforce/apex/DisneyAgentController.getMetrics';


export default class DisneyAssistant extends LightningElement {

    message = '';
    answer = '';
    traceId = '';
    latencyMs = 0;

    activeTab = 'chat';
    isLoading = false;

    @track trace;
    @track metrics;

    selectedAgents = [];

    handleMessageChange(event) {
        this.message = event.target.value;
    }

    handleTraceIdChange(event) {
        this.traceId = event.target.value;
    }

    handleTabChange(event) {
        this.activeTab = event.target.value;
    }

    async handleSend() {

        if (!this.message || this.isLoading) {
            return;
        }

        this.isLoading = true;

        try {

            const result = await chat({
                message: this.message,
                sessionId: 'salesforce-session'
            });

            this.answer = result.answer;
            this.traceId = result.trace_id;
            this.latencyMs = result.latency_ms;

            await this.loadTrace();

        } catch (error) {

            this.answer =
                error?.body?.message || error.message;

        } finally {

            this.isLoading = false;

        }
    }

    async loadTrace() {

        if (!this.traceId) {
            return;
        }

        try {

            const result = await getTrace({
                traceId: this.traceId
            });

            this.trace = JSON.parse(result);

            this.selectedAgents =
                this.trace.selected_agents || [];

        } catch (error) {

            console.error('Trace error', error);

        }
    }

    async loadMetrics() {

        try {

            const result = await getMetrics();

            this.metrics = JSON.parse(result);

        } catch (error) {

            console.error('Metrics error', error);

        }
    }

}