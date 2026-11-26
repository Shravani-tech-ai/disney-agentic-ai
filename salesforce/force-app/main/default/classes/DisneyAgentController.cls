public with sharing class DisneyAgentController {
    @AuraEnabled(cacheable=true)
    public static List<DisneyAgentConfigService.AgentInfo> getAgents() { return DisneyAgentConfigService.getEnabledAgents(); }
    @AuraEnabled
    public static Map<String,Object> chat(String message, String sessionId) {
        if (String.isBlank(message)) throw new AuraHandledException('Please enter a message.');
        if (message.length() > 4000) throw new AuraHandledException('Please keep your message under 4,000 characters.');
        String sid = String.isBlank(sessionId) ? 'SF-' + UserInfo.getUserId() + '-' + String.valueOf(DateTime.now().getTime()) : sessionId;
        try { return DisneyADKService.sendMessage(sid, message.trim(), UserInfo.getUserId()); }
        catch (Exception e) { throw new AuraHandledException('Unable to contact the Disney assistant: ' + e.getMessage()); }
    }
}
