plugins {
    alias(libs.plugins.kotlin.jvm)
    application
}

repositories {
    mavenCentral()
}

dependencies {
    implementation(project(":lib"))
}

application {
    mainClass.set("com.github.cgund98.schemaregistry.app.consumer.ConsumerKt")
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(21))
    }
}
