
import { LightningElement } from 'lwc';

import chat from
    '@salesforce/apex/DisneyAgentController.chat';

import getTrace from
    '@salesforce/apex/DisneyAgentController.getTrace';

import getMetrics from
    '@salesforce/apex/DisneyAgentController.getMetrics';


export default class DisneyAssistant extends LightningElement {

    message = '';

    // Conversation history
    messages = [];

    // Keep the same session for the conversation
    sessionId = 'salesforce-session';

    traceId = '';
    latencyMs = 0;

    activeTab = 'chat';

    isLoading = false;
    isTraceLoading = false;
    isMetricsLoading = false;

    trace;
    metrics;

    selectedAgents = [];

    // Unique message ID counter
    messageCounter = 0;

    get hasMessages() {
        return this.messages.length > 0;
    }

    get hasSelectedAgents() {
        return this.selectedAgents.length > 0;
    }

    get isSendDisabled() {
        return this.isLoading || !this.message.trim();
    }

    get traceLatencySeconds() {
        return this.trace?.latency_ms != null
            ? (this.trace.latency_ms / 1000).toFixed(2)
            : '0.00';
    }

    get averageLatencySeconds() {
        return this.metrics?.average_latency_ms != null
            ? (this.metrics.average_latency_ms / 1000).toFixed(2)
            : '0.00';
    }

    get p95LatencySeconds() {
        return this.metrics?.p95_latency_ms != null
            ? (this.metrics.p95_latency_ms / 1000).toFixed(2)
            : '0.00';
    }

    get traceEvents() {
        return (this.trace?.events || []).map(event => ({
            ...event,
            durationSeconds: event.duration_ms != null
                ? (event.duration_ms / 1000).toFixed(2)
                : '0.00'
        }));
    }

    handleMessageChange(event) {
        this.message = event.target.value;
    }

    handleTraceIdChange(event) {
        this.traceId = event.target.value;
    }

    handleTabChange(event) {
        this.activeTab = event.target.value;
    }

    // Create a message object
    createMessage(sender, text, options = {}) {

        this.messageCounter += 1;

        return {
            id: 'message-' + this.messageCounter,
            sender: sender,
            text: text,
            cssClass: options.isUser
                ? 'message user-message'
                : 'message assistant-message',
            meta: options.meta || '',
            agentInfo: options.agentInfo || '',
            mockNote: options.mockNote || false
        };
    }

    // Add a message to conversation
    addMessage(sender, text, options = {}) {

        const newMessage = this.createMessage(
            sender,
            text,
            options
        );

        this.messages = [
            ...this.messages,
            newMessage
        ];

        this.scrollToBottom();
    }

    // Automatically scroll to latest message
    scrollToBottom() {

        requestAnimationFrame(() => {

            const chatWindow =
                this.refs?.chatWindow;

            if (chatWindow) {
                chatWindow.scrollTop =
                    chatWindow.scrollHeight;
            }

        });
    }

    // Send user message
    async handleSend() {

        const userMessage = this.message.trim();

        if (!userMessage || this.isLoading) {
            return;
        }

        // Display user's question immediately
        this.addMessage(
            'You',
            userMessage,
            { isUser: true }
        );

        // Clear input
        this.message = '';

        this.isLoading = true;

        try {

            const result = await chat({

                message: userMessage,

                sessionId: this.sessionId

            });

            const answer =
                result.answer ||
                'I could not generate a response. Please try again.';

            this.traceId = result.trace_id || '';

            this.latencyMs = result.latency_ms || 0;

            this.selectedAgents =
                result.selected_agents || [];

            const agentInfo = this.selectedAgents.length
                ? 'Agents: ' + this.selectedAgents.join(', ')
                : '';

            const metaParts = [];

            if (this.traceId) {
                metaParts.push('Trace ID: ' + this.traceId);
            }

            metaParts.push(
                'Latency: ' + (this.latencyMs / 1000).toFixed(2) + ' s'
            );

            this.addMessage(
                'Disney Assistant',
                answer,
                {
                    agentInfo: agentInfo,
                    meta: metaParts.join(' | '),
                    mockNote: result.mock === true
                }
            );

            // Automatically load latest execution trace
            if (this.traceId) {
                await this.loadTrace();
            }

        } catch (error) {

            const errorMessage =
                error?.body?.message ||
                error?.message ||
                'Something went wrong. Please try again.';

            this.addMessage(
                'Disney Assistant',
                'Sorry, I encountered an error: ' + errorMessage
            );

        } finally {

            this.isLoading = false;

            this.scrollToBottom();

        }
    }

    // Retrieve trace information
    async loadTrace() {

        if (!this.traceId || this.isTraceLoading) {
            return;
        }

        this.isTraceLoading = true;

        try {

            const result = await getTrace({

                traceId: this.traceId

            });

            this.trace = JSON.parse(result);

            this.selectedAgents =
                this.trace.selected_agents || [];

        } catch (error) {

            console.error(
                'Trace error',
                error
            );

        } finally {

            this.isTraceLoading = false;

        }
    }

    // Retrieve performance metrics
    async loadMetrics() {

        this.isMetricsLoading = true;

        try {

            const result = await getMetrics();

            this.metrics = JSON.parse(result);

        } catch (error) {

            console.error(
                'Metrics error',
                error
            );

        } finally {

            this.isMetricsLoading = false;

        }
    }

}
