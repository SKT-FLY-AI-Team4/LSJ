import React from 'react';
import { StyleSheet, TouchableOpacity, Text, View } from 'react-native';
import { Stack, useRouter, useSegments } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
// import LottieView from 'lottie-react-native';
import { Video } from 'expo-av';

export default function RootLayout() {
  const router = useRouter();
  const segments = useSegments();
  const isChatOpen = segments[segments.length - 1] === 'chat';

  return (
    <View style={{ flex: 1 }}>
      <StatusBar style="dark" />

      <Stack>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen 
          name="chat" 
          options={{
            presentation: 'formSheet', 
            headerShown: false,
            animation: 'fade',
            gestureEnabled: false,
          }} 
        />
        <Stack.Screen name="profile" options={{ presentation: 'modal' }} />
      </Stack>
      
      {/* 기존 플로팅 채팅 버튼 */}
      { !isChatOpen && (
        <TouchableOpacity 
          style={styles.floatingButton} 
          onPress={() => router.push('/chat')}
        >
          <Text style={styles.floatingIcon}>💬</Text>
        </TouchableOpacity>
      )}

      {/* 채팅창이 아닐 때만 보이는 하단 애니메이션 - Lottie 버전
      { !isChatOpen && (
        <LottieView
          source={require('../assets/cat-wave.json')} // 사용할 .json 파일
          style={styles.bottomAnimation}
          autoPlay
          loop
        />
      )} */}

      {/* 채팅창이 아닐 때만 보이는 하단 애니메이션 - Video 버전 */}
      
      { !isChatOpen && (
        <Video
          source={require('../assets/yammi_welcome_mouth_chcek.mp4')} // 사용할 .mp4 파일
          style={styles.bottomAnimation}
          shouldPlay
          isLooping
          isMuted
          resizeMode="contain"
        />
      )}
      
    </View>
  );
}

const styles = StyleSheet.create({
  floatingButton: { 
    position: 'absolute', 
    bottom: 120, 
    right: 30, 
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
  bottomAnimation: {
    width: 150,
    height: 150,
    position: 'absolute',
    bottom: 100, // 위치 조절
    alignSelf: 'center',
    pointerEvents: 'none',
  }
});