import React from 'react';
import { StyleSheet, TouchableOpacity, Text, View } from 'react-native';
// 1. useRouter와 함께 useSegments를 import 합니다.
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  const router = useRouter();
  // 2. 현재 활성화된 경로를 배열 형태로 가져옵니다.
  const segments = useSegments();
  
  // 3. 현재 경로의 마지막 부분이 'chat'인지 확인합니다.
  //    채팅창이 열려있으면 isChatOpen은 true가 됩니다.
  const isChatOpen = segments[segments.length - 1] === 'chat';

  return (
    <View style={{ flex: 1 }}>
      <StatusBar style="dark" />

      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen 
            name="chat" 
            options={{presentation: 'formSheet', 
                      headerShown: false ,
                      animation : 'fade',
                      gestureEnabled: false, // 이 줄을 스와이프 닫기 비활성화
             }} 
        />
      </Stack>
      
      {/* 4. isChatOpen이 false일 때만 (채팅창이 닫혀있을 때만) 버튼을 보여줍니다. */}
      { !isChatOpen && (
        <TouchableOpacity 
          style={styles.floatingButton} 
          onPress={() => router.push('/chat')}
        >
          <Text style={styles.floatingIcon}>💬</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
    floatingButton: { 
        position: 'absolute', 
        bottom: 80, 
        right: 20, 
        width: 60, 
        height: 60, 
        backgroundColor: '#FFBF00', 
        borderRadius: 30, 
        justifyContent: 'center', 
        alignItems: 'center', 
        elevation: 8, 
        zIndex: 10
    },
    floatingIcon: { fontSize: 28 },
});