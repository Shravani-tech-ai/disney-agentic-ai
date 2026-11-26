public with sharing class DisneyAgentConfigService {
    public class AgentInfo {
        @AuraEnabled public String name;
        @AuraEnabled public String intent;
        @AuraEnabled public String description;
        @AuraEnabled public String category;
        @AuraEnabled public Integer displayOrder;
        @AuraEnabled public Boolean active;
    }
    public static List<AgentInfo> getEnabledAgents() {
        List<AgentInfo> result = new List<AgentInfo>();
        Map<String, Boolean> enabledByIntent = new Map<String, Boolean>();
        for (Disney_Intent_Routing__mdt route : [SELECT Intent__c, Is_Enabled__c FROM Disney_Intent_Routing__mdt]) {
            enabledByIntent.put(route.Intent__c, route.Is_Enabled__c);
        }
        for (Disney_Agent_Config__mdt row : [SELECT Agent_Name__c, Intent__c, Description__c, Agent_Category__c, Display_Order__c, Is_Active__c FROM Disney_Agent_Config__mdt WHERE Is_Active__c = true ORDER BY Display_Order__c ASC]) {
            if (enabledByIntent.get(row.Intent__c) == true) {
                AgentInfo info = new AgentInfo(); info.name=row.Agent_Name__c; info.intent=row.Intent__c; info.description=row.Description__c; info.category=row.Agent_Category__c; info.displayOrder=row.Display_Order__c == null ? 0 : row.Display_Order__c.intValue(); info.active=true; result.add(info);
            }
        }
        return result;
    }
    public static Disney_Integration_Config__mdt getIntegrationConfig() {
        List<Disney_Integration_Config__mdt> rows = [SELECT Mock_Mode__c, Timeout_Seconds__c, Retry_Count__c, Is_Active__c FROM Disney_Integration_Config__mdt WHERE DeveloperName = 'Default' LIMIT 1];
        return rows.isEmpty() ? null : rows[0];
    }
}
