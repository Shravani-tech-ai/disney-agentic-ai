import { LightningElement, track } from 'lwc';
import getAgents from '@salesforce/apex/DisneyAgentController.getAgents';
import chat from '@salesforce/apex/DisneyAgentController.chat';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class DisneyAssistant extends LightningElement {
    @track messages = [{ id: 'welcome', label: 'Disney Assistant', text: 'Hello! I can help with product knowledge, Friends & Family duplicates, reservation claims, dining availability and Lightning Lane availability.', cssClass: 'message assistant-message' }];
    @track agents = [];
    draft = ''; loading = false; sessionId;
    connectedCallback() {
        getAgents().then((rows) => { this.agents = rows || []; }).catch((error) => this.toast('Configuration error', this.errorMessage(error), 'error'));
    }
    get sendDisabled() { return this.loading || !this.draft.trim(); }
    handleDraft(event) { this.draft = event.target.value; }
    handleKeydown(event) { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); this.sendMessage(); } }
    async sendMessage() {
        const message = this.draft.trim(); if (!message || this.loading) return;
        this.messages = [...this.messages, { id: `u-${Date.now()}`, label: 'You', text: message, cssClass: 'message user-message' }];
        this.draft = ''; this.loading = true;
        try {
            const result = await chat({ message, sessionId: this.sessionId });
            this.sessionId = result.session_id || this.sessionId;
            this.messages = [...this.messages, { id: `a-${Date.now()}`, label: 'Disney Assistant', text: result.answer || 'The assistant returned no text.', intent: result.intent, mock: result.mock === true, cssClass: 'message assistant-message' }];
        } catch (error) { this.toast('Unable to get a response', this.errorMessage(error), 'error'); }
        finally { this.loading = false; }
    }
    errorMessage(error) { return error?.body?.message || error?.message || 'Unexpected error'; }
    toast(title, message, variant) { this.dispatchEvent(new ShowToastEvent({ title, message, variant })); }
}
