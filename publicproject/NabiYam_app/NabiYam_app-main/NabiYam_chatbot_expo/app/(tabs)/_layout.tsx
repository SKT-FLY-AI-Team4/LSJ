import React from 'react';
import { Tabs } from 'expo-router';
import { FontAwesome } from '@expo/vector-icons';

// 아이콘을 보여주기 위한 헬퍼 컴포넌트
function TabBarIcon(props: { name: React.ComponentProps<typeof FontAwesome>['name']; color: string }) {
  return <FontAwesome size={28} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  return (

    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#4A90E2',
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'HOME',
          headerShown: false, // 각 탭의 헤더는 숨깁니다.
          tabBarIcon: ({ color }) => <TabBarIcon name="home" color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          headerShown: false,
          tabBarIcon: ({ color }) => <TabBarIcon name="compass" color={color} />,
        }}
      />
    </Tabs>
  );
}